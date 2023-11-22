from sqlalchemy.orm import Session

from app.models.payment import Payment
from app.repository.base import BaseRepository
from app.schema.payment import PaymentCreate, PaymentUpdate


class PaymentRepository(
    BaseRepository[Payment, PaymentCreate, PaymentCreate | PaymentUpdate]
):
    def get_by_mpesa_ref_number(
        self, db: Session, mpesa_ref_number: str
    ) -> Payment | None:
        return (
            db.query(Payment)
            .filter(Payment.mpesa_ref_number == mpesa_ref_number)
            .first()
        )


# we can rename this 😼
payment = PaymentRepository(Payment)
