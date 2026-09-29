from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Payment:
    id: int
    customer_id: int
    invoice_id: int
    amount: Decimal
    method: str
    status: str
    transaction_id: str | None = None