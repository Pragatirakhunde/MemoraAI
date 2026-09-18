from dataclasses import dataclass


@dataclass
class ExtractedEntity:
    name: str
    entity_type: str
    confidence: float
    source_text: str