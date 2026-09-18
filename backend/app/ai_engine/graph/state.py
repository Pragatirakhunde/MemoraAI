from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    query: str
    organization_id: int
    conversation_history: list[dict[str, Any]]

    entities: list[dict[str, Any]]
    vector_results: list[dict[str, Any]]
    graph_results: list[dict[str, Any]]
    fused_context: list[dict[str, Any]]

    prompt: str
    answer: str
    references: list[dict[str, Any]]

    error: str | None