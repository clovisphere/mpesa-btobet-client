import decimal

from sqlalchemy import Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base
from app.models.mixins import Status, Timestamp


class Payment(Timestamp, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.PENDING)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(10, 2))
    org_account_balance: Mapped[decimal.Decimal] = mapped_column(
        Numeric(10, 2), nullable=True
    )
    transaction_type: Mapped[str] = mapped_column(String(30))
    mpesa_ref_number: Mapped[str] = mapped_column(
        String(30), unique=True, index=True, nullable=False
    )
    msisdn: Mapped[str] = mapped_column(String(15), nullable=True)
    comment: Mapped[str] = mapped_column(Text, nullable=True)

    # relationship / foreign key 🔑
    profile_id: Mapped[int] = mapped_column(ForeignKey("profile.id"), nullable=True)
