from datetime import datetime

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    name: str
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    organization_id: int
    name: str
    email: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)