from decimal import Decimal

from app.repositories.payment_repository import PaymentRepository
from app.services.payment_service import PaymentService


repository = PaymentRepository()
payment_service = PaymentService(repository)


def create_payment(
    payment_id: int,
    customer_id: int,
    invoice_id: int,
    amount: float,
    method: str,
):
    return payment_service.create_payment(
        payment_id=payment_id,
        customer_id=customer_id,
        invoice_id=invoice_id,
        amount=Decimal(str(amount)),
        method=method,
    )


def get_payment(payment_id: int):
    payment = payment_service.get_payment(payment_id)

    if payment is None:
        return {
            "error": "Payment not found",
        }

    return payment