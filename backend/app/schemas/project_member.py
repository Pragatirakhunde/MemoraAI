from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict


class ProjectMemberCreate(BaseModel):
    user_id: int
    permission: Literal[
        "PROJECT_MEMBER",
        "PROJECT_VIEWER",
    ] = "PROJECT_MEMBER"


class ProjectMemberResponse(BaseModel):
    id: int
    project_id: int
    user_id: int
    permission: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)