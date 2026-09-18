from typing import Any

from pydantic import BaseModel, Field


class AIChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    conversation_id: int | None = None


class AIChatResponse(BaseModel):
    conversation_id: int
    query: str
    answer: str
    references: list[dict[str, Any]]
    entities: list[dict[str, Any]]