from dataclasses import dataclass
from decimal import Decimal


@dataclass
class Invoice:
    id: int
    customer_id: int
    invoice_number: str
    amount: Decimal
    currency: str = "INR"
    paid: bool = False