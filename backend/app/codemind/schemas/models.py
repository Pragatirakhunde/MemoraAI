from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class CodeRepositoryCreate(BaseModel):
    project_id: int
    name: str = Field(min_length=2, max_length=200)
    provider: str = Field(pattern=r"^(local|github)$")
    local_path: str | None = None
    remote_url: str | None = None
    default_branch: str = "main"
    description: str | None = None


class CodeRepositoryResponse(BaseModel):
    id: int
    organization_id: int
    project_id: int
    name: str
    provider: str
    remote_url: str | None
    local_path: str | None
    default_branch: str
    description: str | None
    status: str
    index_status: str
    last_indexed_at: datetime | None
    last_index_error: str | None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class CodeAskRequest(BaseModel):
    query: str = Field(min_length=2, max_length=4000)
    limit: int = Field(default=8, ge=1, le=20)


class CodeSearchRequest(BaseModel):
    query: str = Field(min_length=2, max_length=2000)
    limit: int = Field(default=10, ge=1, le=30)


class BusinessRuleRequest(BaseModel):
    rule: str = Field(min_length=3, max_length=3000)
    limit: int = Field(default=8, ge=1, le=20)
