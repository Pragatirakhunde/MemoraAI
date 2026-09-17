from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DataSourceCreate(BaseModel):
    name: str
    source_type: str
    config: dict


class DataSourceResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    source_type: str
    config: dict
    status: str
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)