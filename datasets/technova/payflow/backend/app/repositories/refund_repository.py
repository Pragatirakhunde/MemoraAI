from app.models.refund import Refund


class RefundRepository:
    def __init__(self) -> None:
        self._refunds: dict[int, Refund] = {}

    def save(self, refund: Refund) -> Refund:
        self._refunds[refund.id] = refund
        return refund

    def get_by_id(self, refund_id: int) -> Refund | None:
        return self._refunds.get(refund_id)

    def get_by_payment_id(
        self,
        payment_id: int,
    ) -> list[Refund]:
        return [
            refund
            for refund in self._refunds.values()
            if refund.payment_id == payment_id
        ]