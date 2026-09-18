from pydantic import BaseModel


class ProjectContextResponse(BaseModel):
    project: str | None
    technologies: list[str]
    databases: list[str]
    modules: list[str]
    documents: list[dict]


class GraphProjectResponse(BaseModel):
    project: str
    technology: str


class GraphDatabaseResponse(BaseModel):
    project: str
    database: str


class ProjectKnowledgeResponse(BaseModel):
    project: str | None
    technologies: list[dict]
    databases: list[dict]
    modules: list[dict]
    documents: list[dict]


class GraphNeighborhoodResponse(BaseModel):
    source_type: list[str]
    source_name: str
    relationship: str | None
    target_type: list[str]
    target_name: str | None