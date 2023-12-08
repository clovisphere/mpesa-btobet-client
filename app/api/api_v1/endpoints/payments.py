import os
import time
from typing import Callable

import httpx
from fastapi import (
    APIRouter,
    BackgroundTasks,
    Depends,
    Header,
    HTTPException,
    Request,
    Response,
    status,
)
from sqlalchemy.orm import Session

from app import repository
from app.config.default import settings
from app.config.logger import logger
from app.deps import get_db_session
from app.helpers.btobet import BTOBET
from app.helpers.cheza import Cheza
from app.helpers.utility import Utility
from app.models.mixins import Status
from app.models.payment import Payment
from app.schema.profile import ProfileCreate
from app.template.error import INVALID_MSISDN
from app.template.broker_response import (
    BROKER_CONFIRMATION_RESPONSE_TEMPLATE,
    BROKER_VALIDATION_RESPONSE_TEMPLATE,
)
from app.template.cheza_sms import (
    DEPOSIT_SMS_FAILURE_MESSAGE,
    DEPOSIT_SMS_GENERIC_MESSAGE,
    DEPOSIT_SMS_SUCCESS_MESSAGE,
)

router = APIRouter()


class CustomXMLReponse(Response):
    media_type = "text/xml"


@router.post("/validation", response_class=CustomXMLReponse, status_code=status.HTTP_202_ACCEPTED)
def validate(request: Request, content_type: str | None = Header(None)):
    """Validate details of a payment before accepting it."""
    if content_type in settings.XML_ALLOWED_CONTENT_TYPE:
        response: str = BROKER_VALIDATION_RESPONSE_TEMPLATE.format(
            RESULT_CODE=0,
            RESULT_DESCRIPTION="Success",
            THIRD_PARTY_TRANSACTION_ID=time.time_ns(),
        )
        return CustomXMLReponse(content=response)
    logger.error("could not process the request 😪")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="request cannot be processed."
    )


@router.post("/confirmation", response_class=CustomXMLReponse, status_code=status.HTTP_201_CREATED)
async def confirm(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    content_type: str | None = Header(None),
):
    """Accept payments successfully processed on Safaricom's end."""
    # message to return when we have a failure:-)
    message: str = settings.BROKER_FAILURE_MESSAGE
    if content_type in settings.XML_ALLOWED_CONTENT_TYPE:
        body: bytes = await request.body()
        req = Utility.parse_confirmation_request(body.decode("utf-8"))
        if req and req["TransID"]:
            logger.debug(f"[{req['TransID']}] | request received {req}")
            message = settings.BROKER_SUCCESS_MESSAGE.format(
                TRANSACTION_ID=req["TransID"]
            )
            background_tasks.add_task(
                process_confirm_request,
                payment_details=req,
                session=db
            )
            response = BROKER_CONFIRMATION_RESPONSE_TEMPLATE.format(MESSAGE=message)
            return CustomXMLReponse(content=response)
    logger.error("could not process the request 😪 ")
    raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

async def process_confirm_request(payment_details: dict[str, str], session: Session) -> None:
    logger.info(f"[{payment_details['TransID']}] | procesing request... ")
    # let's create a payment obj with known field 🤭
    payment = BTOBET.make_payment_obj(payment_details)
    msisdn, known_profile = await fetch_msisdn_from_profile(payment_details, session)
    # we can't proceed if the MSISDN is invalid:(
    if not msisdn:
        logger.error(
            f"[{payment_details['TransID']}] | unable to process request. "
            +"MSISDN/BillRefNumber is an invalid MSISDN"
        )
        payment.status = Status.INTERNAL_ERROR
        payment.comment = INVALID_MSISDN.format(
            HASHED_MSISDN=payment_details["MSISDN"],
            BILL_REF_NUMBER=payment_details["BillRefNumber"]
        )
        logger.info(f"[{payment.mpesa_ref_number}] | saving request | {payment.status} ")
        repository.payment.create(session, obj_in=payment)
        return  # it's okay to return 😊
    # create profile (if possible)
    if msisdn and not known_profile:
        if payment_details["MSISDN"] == Utility.hash_mobile_number(msisdn):
            profile = await create_new_profile(payment_details, session)
            if profile:
                payment.profile_id = profile.id
    # checking if a similar request exist
    obj, already_processed = await get_payment_or_none(payment_details["TransID"], session)
    # if the request has already been processed, return
    if already_processed:
        return

    #==========================================💫✨💫✨=====================================#
    #                                                                                       #
    #                                         START JOB                                     #
    #                                                                                       #
    #==========================================💫✨💫✨=====================================#

    # if we get here, then we can process the request 🤓
    payment.msisdn = msisdn
    # we may have the request/transaction but not in a final state
    existing_req: bool = True if obj else False
    # let's have a generic sms message (just in case)
    message = DEPOSIT_SMS_GENERIC_MESSAGE

    try:
        logger.info(f"[{payment.mpesa_ref_number}] | building (confirmation) payload ")
        payload = BTOBET.build_broker_deposit_payload(payment)
        endpoint = os.environ.get("BTOBET_DEPOSIT_PROCESS_URL", "")
        logger.info(
            f"[{payment.mpesa_ref_number}] | "
            f"sending (confirmation) payload to btobet... "
        )
        response = BTOBET.send_to_btobet(url=endpoint, payload=payload)
        logger.info(
            f"[{payment.mpesa_ref_number}] | " f"response from btobet: {response} ",
        )
        payment.status = (
            Status.ACCEPTED_BY_BTOBET
            if int(response["StatusCode"]) == 0
            else Status.REJECTED_BY_BTOBET
        )
        # what message/sms do we send the user/client?
        message = (
            DEPOSIT_SMS_FAILURE_MESSAGE
            if payment.status == Status.REJECTED_BY_BTOBET
            else DEPOSIT_SMS_SUCCESS_MESSAGE
        )
        # register customer if we got a 3201
        if int(response["StatusCode"]) == settings.FAILED_REGISTRATION_STATUS_CODE:
            logger.info(
                f"[{payment.mpesa_ref_number}] | "
                f"customer with mobile number: {payment.msisdn} "
                + " is not a registered cutomer. "
                + "We'll attempt to register him/her. "
            )
            reg_payload = {
                "phone_number": payment.msisdn,
                "request_id": payment.mpesa_ref_number,
            }
            # # (I think there's a better way to handle this 🫣)
            await handler(
                Cheza.register_customer, payment.mpesa_ref_number, reg_payload
            )
    except KeyError as e:
        logger.error(f"[{payment.mpesa_ref_number}] | KeyError: {e} ")
        payment.status = Status.INTERNAL_ERROR
        payment.comment = f"Error: {e}"
    except (httpx.HTTPError, Exception) as e:
        logger.error(f"[{payment.mpesa_ref_number}] | an exception occurred: {e} ")
        payment.status = Status.UNKNOWN_BTOBET_STATUS
        payment.comment = "Error: we are unable to call/hit BtoBET 😪"
    finally:
        # send sms to the end-user/customer/client 🤓
        logger.info(f"[{payment.mpesa_ref_number}] | notifying customer 📝 ")
        sms_payload = {
            "phone_number": payment.msisdn,
            "message": message,
            "mpesa_ref_number": payment.mpesa_ref_number,
        }
        # (I think there's a better way to handle this 🫣)
        await handler(Cheza.send_sms, payment.mpesa_ref_number, sms_payload)
        if existing_req and obj:
            logger.info(
                f"[{payment.mpesa_ref_number}] | "
                f"updating request | {payment.status} "
            )
            repository.payment.update(session, db_obj=obj, obj_in=payment)
            return
        logger.info(
            f"[{payment.mpesa_ref_number}] | saving request | {payment.status} "
        )
        repository.payment.create(session, obj_in=payment)


async def fetch_msisdn_from_profile(
    payment_details: dict[str, str], session: Session
) -> tuple[str, bool]:
    logger.info(
        f"[{payment_details['TransID']}] | "
        +"checking whether the request's (hashed) MSISDN is known 😊 "
    )
    profile = repository.profile.get_profile_by_hashed_msisdn(session, payment_details["MSISDN"])
    if profile is None:
        logger.info(
            f"[{payment_details['TransID']}] | unknown (hashed) MSISDN 😪, "
            +"we will attempt to use the `BillRefNumber` (if any) "
            f"~> {payment_details['BillRefNumber']} "
        )
        return Utility.rewrite_mobile_number(payment_details["BillRefNumber"]), False
    logger.info(f"[{payment_details['TransID']}] the (hashed) MSISDN is known to us 👏🏽 ")
    return profile.msisdn, True  # we have a profile with this hashed MSISDN

async def create_new_profile(payment_details: dict[str, str], session: Session) -> None:
    logger.info(f"[{payment_details['TransID']}] | creating a profile for (hashed) MSISDN ")

    profile = ProfileCreate(
        msisdn=payment_details["BillRefNumber"],
        hashed_msisdn=payment_details["MSISDN"]
    )
    result = repository.profile.create(session, obj_in=profile)
    if result is None:
        logger.error(
            f"[{payment_details['TransID']}] | "
            +"couldn't create profile for the given (hashed) MSISDN 😪 ")
        return
    logger.info(f"[{payment_details['TransID']}] | profile created 🥳 ")

async def get_payment_or_none(mpesa_ref_number: str, session: Session) -> tuple[None|Payment, bool]:
    already_processed: bool = False
    payment = repository\
                .payment\
                .get_by_mpesa_ref_number(
                    session,
                    mpesa_ref_number=mpesa_ref_number
                )
    if payment:
        if payment.status in (Status.ACCEPTED_BY_BTOBET, Status.REJECTED_BY_BTOBET, Status.INTERNAL_ERROR):
            logger.info(f"[{mpesa_ref_number}] | "
                f"request has already been processed ({payment.status}), "
                + "nothing to do 🫡 ")
            already_processed = True
        else:
            logger.info(
                f"[{mpesa_ref_number}] | "
                f"request not in a final state: ({payment.status}), "
                +"we'll attempt to repocess it ")
    return payment, already_processed

async def handler(fn: Callable, mpesa_ref_number: str, payload: dict) -> None:
    """Used to run tasks that are not THAT IMPORTANT 🤪"""
    try:
        logger.info(f"[{mpesa_ref_number}] | " f"invoking '{fn.__name__}'... ")
        response = fn(**payload)  # fn can either be `register_customer` or `send_sms`
        logger.info(
            f"[{mpesa_ref_number}] | "
            f"response from '{fn.__name__}', if any 😜 ~> {response} "
        )
    except Exception as e:
        logger.error(f"[{mpesa_ref_number}] | an exception occurred: {e} ")
