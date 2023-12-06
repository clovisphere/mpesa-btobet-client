import datetime
import enum

from sqlalchemy import DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm.decl_api import declarative_mixin
from sqlalchemy.sql import func


# we can probably change it to a table? 😾
class Status(enum.StrEnum):
    # GENERIC
    PENDING = "PENDING"
    INTERNAL_ERROR = "INTERNAL_ERROR"
    # BTOBET STATUSES
    ACCEPTED_BY_BTOBET = "ACCEPTED_BY_BTOBET"
    REJECTED_BY_BTOBET = "REJECTED_BY_BTOBET"
    UNKNOWN_BTOBET_STATUS = "UNKNOWN_BTOBET_STATUS"


@declarative_mixin
class Timestamp:
    created_on: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )

    updated_on: Mapped[datetime.datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
