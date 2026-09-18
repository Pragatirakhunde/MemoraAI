from dataclasses import dataclass


@dataclass
class ExtractedRelationship:
    source_name: str
    source_type: str
    relationship_type: str
    target_name: str
    target_type: str
    confidence: float
    source_text: str
    