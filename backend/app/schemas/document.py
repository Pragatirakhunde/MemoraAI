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
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentResponse(DocumentListResponse):
    content: str
    metadata_json: dict