from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1)
    limit: int = Field(default=5, ge=1, le=20)

    document_type: str | None = None
    language: str | None = None
    data_source_id: int | None = None
    extension: str | None = None


class SearchReference(BaseModel):
    document_id: int
    chunk_id: int
    title: str
    file_path: str
    extension: str
    document_type: str | None
    language: str | None
    chunk_index: int
    score: float


class SearchResult(BaseModel):
    score: float
    document_id: int
    chunk_id: int
    title: str
    content: str
    reference: SearchReference