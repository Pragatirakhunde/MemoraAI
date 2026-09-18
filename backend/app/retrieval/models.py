from dataclasses import dataclass, field


@dataclass
class VectorResult:
    document_id: int
    chunk_id: int
    title: str
    content: str
    score: float
    file_path: str
    reference: dict


@dataclass
class GraphResult:
    entity_name: str
    entity_type: str
    relationship: str | None
    related_name: str | None
    related_type: list[str] = field(
        default_factory=list
    )
    source_document_id: int | None = None
    hops: int = 1
    confidence: float = 0.8


@dataclass
class HybridRetrievalResult:
    query: str
    vector_results: list[VectorResult]
    graph_results: list[GraphResult]
    entities: list[dict]


@dataclass
class FusedContextItem:
    source_type: str
    score: float
    content: str
    reference: dict