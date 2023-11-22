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


@router.post("/validation")
def validate(request: Request, content_type: str | None = Header(None)):
    """Validate details of a payment before accepting it."""
    if content_type in settings.XML_ALLOWED_CONTENT_TYPE:
        response: str = BROKER_VALIDATION_RESPONSE_TEMPLATE.format(
            RESULT_CODE=0,
            RESULT_DESCRIPTION="Success",
            THIRD_PARTY_TRANSACTION_ID=time.time_ns(),
        )
        return Response(
            content=response,
            status_code=status.HTTP_202_ACCEPTED,
            media_type=content_type,
        )
    logger.error("could not process the request 😪")
    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST, detail="request cannot be processed."
    )


@router.post("/confirmation")
async def confirm(
    request: Request,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session),
    content_type: str | None = Header(None),
):
    """Accept payments successfully processed on Safaricom's end."""
    # message and status to return when we have a failure:-)
    message: str = settings.BROKER_FAILURE_MESSAGE
    http_code: int = status.HTTP_400_BAD_REQUEST

    if content_type in settings.XML_ALLOWED_CONTENT_TYPE:
        body: bytes = await request.body()
        req = Utility.parse_confirmation_request(body.decode("utf-8"))
        logger.debug(f"[{req['TransID']}] | request received {req}")
        if req and req["TransID"]:
            message = settings.BROKER_SUCCESS_MESSAGE.format(
                TRANSACTION_ID=req["TransID"]
            )
            http_code = status.HTTP_201_CREATED
            background_tasks.add_task(
                process_confirm_request, payment_details=req, session=db
            )
        response = BROKER_CONFIRMATION_RESPONSE_TEMPLATE.format(MESSAGE=message)
        return Response(
            content=response, status_code=http_code, media_type=content_type
        )
    logger.error("could not process the request 😪 ")
    raise HTTPException(status_code=http_code, detail=message)


async def process_confirm_request(
    payment_details: dict[str, str], session: Session
) -> None:
    logger.info(f"[{payment_details['TransID']}] | procesing request... ")
    # checking if a similar request exist
    existing_req: bool = False
    obj = repository.payment.get_by_mpesa_ref_number(
        session, mpesa_ref_number=payment_details["TransID"]
    )
    if obj:
        if obj.status in (
            Status.ACCEPTED_BY_BTOBET,
            Status.REJECTED_BY_BTOBET,
            Status.CLIENT_ERROR,
        ):
            logger.info(
                f"[{payment_details['TransID']}] | "
                f"request has already been processed ({obj.status}), "
                "nothing to do 🫡 "
            )
            return  # it's okay to return 🤗
        else:
            logger.info(
                f"[{payment_details['TransID']}] | "
                f"request not in a final status: ({obj.status}), "
                "we'll attempt to repocess it "
            )
            existing_req = True
    # let's have a generic sms message
    message = DEPOSIT_SMS_GENERIC_MESSAGE
    # we can safely create a payment object at this point:-)
    payment = BTOBET.make_payment_obj(payment_details)

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
                f"customer with mobile number: {payment.mobile_number} "
                + " is not a registered cutomer. "
                + "We'll attempt to register him/her. "
            )
            reg_payload = {
                "phone_number": payment.mobile_number,
                "request_id": payment.mpesa_ref_number,
            }
            # # (I think there's a better way to handle this 🫣)
            await handler(
                Cheza.register_customer, payment.mpesa_ref_number, reg_payload
            )
    except KeyError as e:
        logger.error(f"[{payment.mpesa_ref_number}] | KeyError: {e} ")
        payment.status = Status.CLIENT_ERROR
    except httpx.HTTPError as e:
        logger.error(f"[{payment.mpesa_ref_number}] | an exception occurred: {e} ")
        payment.status = Status.UNKNOWN_BTOBET_STATUS
    finally:
        # send sms to the end-user/customer/client 🤓
        logger.info(f"[{payment.mpesa_ref_number}] | notifying customer 📝 ")
        sms_payload = {
            "phone_number": payment.mobile_number,
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
            f"[{payment.mpesa_ref_number}] | " f"saving request | {payment.status} "
        )
        repository.payment.create(session, obj_in=payment)


async def handler(fn: Callable, mpesa_ref_number: str, payload: dict) -> None:
    """Used to run tasks that are not THAT IMPORTANT 🤪"""
    try:
        logger.info(f"[{mpesa_ref_number}] | " f"invoking '{fn.__name__}'... ")
        response = fn(**payload)  # func can either be `register_customer` or `send_sms`
        logger.info(
            f"[{mpesa_ref_number}] | "
            f"response from '{fn.__name__}', if any 😜 ~> {response} "
        )
    except httpx.HTTPError as e:
        logger.error(f"[{mpesa_ref_number}] | an exception occurred: {e} ")
