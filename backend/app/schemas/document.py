from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentListResponse(BaseModel):
    id: int
    data_source_id: int
    source_file_id: int
    title: str
    file_path: str
    extension: str
    checksum: str
    status: str
    processing_status: str
    processed_at: datetime | None
    processing_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentListResponse):
    content: str
    metadata_json: dict


class DocumentChunkResponse(BaseModel):
    id: int
    document_id: int
    chunk_index: int
    content: str
    character_count: int
    checksum: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)