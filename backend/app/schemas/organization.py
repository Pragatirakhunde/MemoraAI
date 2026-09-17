from datetime import datetime

from pydantic import BaseModel, ConfigDict


class OrganizationCreate(BaseModel):
    name: str
    slug: str
    description: str | None = None


class OrganizationResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)