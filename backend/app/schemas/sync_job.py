from datetime import datetime

from pydantic import BaseModel, ConfigDict


class SyncJobResponse(BaseModel):
    id: int
    data_source_id: int
    status: str
    started_at: datetime | None
    completed_at: datetime | None
    files_found: int
    files_processed: int
    error_message: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)