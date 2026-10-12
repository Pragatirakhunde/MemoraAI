from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Refund:
    id: int
    payment_id: int
    amount: Decimal
    reason: str
    status: str = "requested"