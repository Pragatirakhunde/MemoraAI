from pydantic import BaseModel


class RetrievalReference(BaseModel):
    source: str
    document_id: int | None = None
    chunk_id: int | None = None
    title: str | None = None
    file_path: str | None = None

    entity: str | None = None
    entity_type: str | None = None
    relationship: str | None = None
    related_entity: str | None = None
    related_type: list[str] | None = None

    retrieval_score: float | None = None
    confidence: float | None = None
    hops: int | None = None


class RetrievalEvidence(BaseModel):
    source_type: str
    score: float
    content: str
    reference: RetrievalReference


class RetrievalEntity(BaseModel):
    name: str
    type: str
    confidence: float


class RetrievalResponse(BaseModel):
    query: str
    entities: list[RetrievalEntity]
    evidence: list[RetrievalEvidence]
    vector_result_count: int
    graph_result_count: int