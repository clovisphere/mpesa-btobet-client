import decimal

from pydantic import BaseModel

from app.models.mixins import Status


class PaymentBase(BaseModel):
    transaction_type: str
    status: Status = Status.PENDING
    mpesa_ref_number: str
    amount: decimal.Decimal
    org_account_balance: decimal.Decimal
    msisdn: str = ""
    comment: str = ""
    profile_id: int | None = None


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(PaymentBase):
    pass


class PaymentInDB(PaymentBase):
    id: int

    class Config:
        from_attributes = True
