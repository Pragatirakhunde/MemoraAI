from app.models.payment import Payment


class PaymentRepository:
    def __init__(self) -> None:
        self._payments: dict[int, Payment] = {}

    def save(self, payment: Payment) -> Payment:
        self._payments[payment.id] = payment
        return payment

    def get_by_id(self, payment_id: int) -> Payment | None:
        return self._payments.get(payment_id)

    def get_by_invoice_id(self, invoice_id: int) -> list[Payment]:
        return [
            payment
            for payment in self._payments.values()
            if payment.invoice_id == invoice_id
        ]