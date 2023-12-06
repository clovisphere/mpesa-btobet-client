from sqlalchemy import String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db import Base
from app.models.mixins import Timestamp
from app.models.payment import Payment


class Profile(Timestamp, Base):
    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    msisdn: Mapped[str] = mapped_column(String(15), nullable=False, index=True)
    hashed_msisdn: Mapped[str] = mapped_column(Text, nullable=False, index=True)

    # one-to-many relationship(s) 😊
    payments: Mapped[list["Payment"]] = relationship(backref="profile")

    # unique constraint 😙
    __table_args__ = (UniqueConstraint("msisdn", "hashed_msisdn", name="unique_profile"),)
