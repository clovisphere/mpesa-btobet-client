import decimal
import hashlib
import os

import httpx

from app.config.default import settings
from app.helpers.utility import Utility
from app.schema.payment import PaymentCreate


class BTOBET:
    @staticmethod
    def send_to_btobet(url: str, payload: dict[str, str | None]):
        with httpx.Client(headers={"Content-Type": "application/json"}) as client:
            response = (
                client.post(url, json=payload, timeout=settings.DEFAULT_TIMEOUT)
                .raise_for_status()
                .json()
            )
        return response

    @staticmethod
    def make_payment_obj(obj: dict[str, str]) -> PaymentCreate:
        return PaymentCreate(
            transaction_type=obj["TransType"],
            mpesa_ref_number=obj["TransID"],
            amount=decimal.Decimal(obj["TransAmount"]),
            org_account_balance=decimal.Decimal(obj["OrgAccountBalance"]),
        )

    @staticmethod
    def build_broker_deposit_payload(payment: PaymentCreate) -> dict[str, str | None]:
        return {
            "AuthToken": BTOBET.md5(str(int(payment.amount))),
            "ClientID": os.getenv("BTOBET_API_CLIENT_ID"),
            "PaymentMethodID": os.getenv("BTOBET_API_PAYMENT_METHOD_ID"),
            "Amount": str(int(payment.amount)),
            "Username": f"0{payment.msisdn[3:]}",
            "Email": None,
            "UserID": None,
            "Currency": os.getenv("CURRENCY"),
            "PspID": payment.mpesa_ref_number,
            "Language": "en",
            "WithdrawalID": None,
            "PosID": None,
            "CashierID": None,
        }

    @staticmethod
    def md5(amount: str) -> str:
        pwd = (
            f"{os.getenv('BTOBET_API_CLIENT_ID')}"
            f"{os.getenv('BTOBET_API_PAYMENT_METHOD_ID')}"
            f"{amount}"
            f"{os.getenv('CURRENCY')}"
            f"{os.getenv('BTOBET_API_SECRET_KEY')}"
        )
        return hashlib.md5(pwd.encode("utf-8")).hexdigest()
