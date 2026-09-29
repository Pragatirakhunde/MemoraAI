from dataclasses import dataclass


@dataclass
class Customer:
    id: int
    name: str
    email: str
    phone: str
    active: bool = True