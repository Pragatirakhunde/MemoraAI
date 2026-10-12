from decimal import Decimal

from app.core.constants import (
    PAYMENT_FAILED,
    PAYMENT_PROCESSING,
    PAYMENT_SUCCESS,
    SUPPORTED_PAYMENT_METHODS,
)
from app.models.payment import Payment
from app.repositories.payment_repository import PaymentRepository


class PaymentService:
    def __init__(self, repository: PaymentRepository) -> None:
        self.repository = repository

    def create_payment(
        self,
        payment_id: int,
        customer_id: int,
        invoice_id: int,
        amount: Decimal,
        method: str,
    ) -> Payment:

        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero.")

        if method not in SUPPORTED_PAYMENT_METHODS:
            raise ValueError(f"Unsupported payment method: {method}")

        payment = Payment(
            id=payment_id,
            customer_id=customer_id,
            invoice_id=invoice_id,
            amount=amount,
            method=method,
            status=PAYMENT_PROCESSING,
        )

        self.repository.save(payment)

        payment.status = PAYMENT_SUCCESS
        payment.transaction_id = f"TXN-{payment_id:06d}"

        return self.repository.save(payment)

    def get_payment(self, payment_id: int) -> Payment | None:
        return self.repository.get_by_id(payment_id)

    def mark_failed(self, payment_id: int) -> Payment:
        payment = self.repository.get_by_id(payment_id)

        if payment is None:
            raise ValueError("Payment not found.")

        payment.status = PAYMENT_FAILED
        return self.repository.save(payment)