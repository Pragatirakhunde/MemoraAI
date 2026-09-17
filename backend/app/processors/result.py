from dataclasses import dataclass


@dataclass
class ProcessingResult:
    document_id: int
    cleaned_text: str
    metadata: dict
    chunks: list[str]