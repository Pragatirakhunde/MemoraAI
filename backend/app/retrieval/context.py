from dataclasses import dataclass


@dataclass
class FusedContextItem:
    source_type: str
    score: float
    content: str
    reference: dict