from decimal import Decimal

from app.models.payment import Payment
from app.models.refund import Refund
from app.repositories.payment_repository import PaymentRepository
from app.repositories.refund_repository import RefundRepository


class RefundService:
    def __init__(
        self,
        payment_repository: PaymentRepository,
        refund_repository: RefundRepository,
    ) -> None:
        self.payment_repository = payment_repository
        self.refund_repository = refund_repository

    def create_refund(
        self,
        refund_id: int,
        payment_id: int,
        amount: Decimal,
        reason: str,
    ) -> Refund:

        if amount <= 0:
            raise ValueError(
                "Refund amount must be greater than zero."
            )

        payment = self.payment_repository.get_by_id(
            payment_id
        )

        if payment is None:
            raise ValueError("Payment not found.")

        if payment.status != "success":
            raise ValueError(
                "Only successful payments can be refunded."
            )

        existing_refunds = (
            self.refund_repository.get_by_payment_id(
                payment_id
            )
        )

        refunded_amount = sum(
            refund.amount
            for refund in existing_refunds
            if refund.status in {"requested", "completed"}
        )

        if refunded_amount + amount > payment.amount:
            raise ValueError(
                "Refund amount exceeds payment amount."
            )

        refund = Refund(
            id=refund_id,
            payment_id=payment_id,
            amount=amount,
            reason=reason,
            status="completed",
        )

        return self.refund_repository.save(refund)

    def get_refund(
        self,
        refund_id: int,
    ) -> Refund | None:
        return self.refund_repository.get_by_id(refund_id)