from fastapi import APIRouter, Depends , HTTPException
from urllib.parse import unquote

from app.api.v1.auth.roles import require_employee
from app.models.user import User
from app.api.v1.auth.dependencies import get_current_user


from app.schemas.graph import (
    GraphDatabaseResponse,
    GraphNeighborhoodResponse,
    GraphProjectResponse,
    ProjectContextResponse,
    ProjectKnowledgeResponse,
)

from app.services.graph_query_service import (
    GraphQueryService,
)


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"],
)


@router.get(
    "/projects",
)
def list_projects(
    current_user: User = Depends(
        require_employee
    ),
):
    return GraphQueryService.list_projects(
        current_user.organization_id,
    )


@router.get(
    "/projects/{project_name}",
    response_model=ProjectContextResponse,
)
def get_project_context(
    project_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(project_name)

    return GraphQueryService.get_project_context(
        organization_id=(
            current_user.organization_id
        ),
        project_name=project_name,
    )


@router.get(
    "/technologies/{technology_name}/projects",
    response_model=list[GraphProjectResponse],
)
def get_projects_using_technology(
    technology_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    technology_name = unquote(
        technology_name
    )

    return (
        GraphQueryService
        .get_projects_using_technology(
            organization_id=(
                current_user.organization_id
            ),
            technology_name=technology_name,
        )
    )


@router.get(
    "/databases/{database_name}/projects",
    response_model=list[GraphDatabaseResponse],
)
def get_projects_using_database(
    database_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    database_name = unquote(
        database_name
    )

    return (
        GraphQueryService
        .get_projects_using_database(
            organization_id=(
                current_user.organization_id
            ),
            database_name=database_name,
        )
    )


@router.get(
    "/entities/{entity_name}/documents",
)
def get_entity_documents(
    entity_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(entity_name)

    return (
        GraphQueryService
        .get_documents_for_entity(
            organization_id=(
                current_user.organization_id
            ),
            entity_name=entity_name,
        )
    )

@router.get(
    "/projects/{project_name}/knowledge",
    response_model=ProjectKnowledgeResponse,
)
def get_project_knowledge(
    project_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(project_name)

    return GraphQueryService.get_project_knowledge(
        organization_id=current_user.organization_id,
        project_name=project_name,
    )


@router.get(
    "/entities/{entity_name}/neighborhood",
    response_model=list[GraphNeighborhoodResponse],
)
def get_entity_neighborhood(
    entity_name: str,
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(entity_name)

    return GraphQueryService.get_entity_neighborhood(
        organization_id=current_user.organization_id,
        entity_name=entity_name,
    )

@router.get("/projects")
def list_projects(
    current_user: User = Depends(get_current_user),
):
    return {
        "projects": GraphQueryService.list_projects(
            organization_id=current_user.organization_id,
        )
    }

@router.get("/project/{project_name}/graph")
def get_project_graph(
    project_name: str,
    current_user: User = Depends(get_current_user),
):
    result = GraphQueryService.get_project_graph(
        organization_id=current_user.organization_id,
        project_name=project_name,
    )

    if not result["nodes"]:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result

@router.get("/project/{project_name}")
def get_project(
    project_name: str,
    current_user: User = Depends(get_current_user),
):
    result = GraphQueryService.get_project_context(
        organization_id=current_user.organization_id,
        project_name=project_name,
    )

    if result["project"] is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result

@router.get("/entity/{entity_name}")
def get_entity(
    entity_name: str,
    current_user: User = Depends(get_current_user),
):
    return {
        "entity": entity_name,
        "relationships": GraphQueryService.get_entity_neighborhood(
            organization_id=current_user.organization_id,
            entity_name=entity_name,
        ),
    }

@router.get("/entity/{entity_name}/expand")
def expand_entity(
    entity_name: str,
    max_hops: int = 2,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
):
    return {
        "entity": entity_name,
        "max_hops": max_hops,
        "results": GraphQueryService.expand_entity(
            organization_id=current_user.organization_id,
            entity_name=entity_name,
            max_hops=max_hops,
            limit=limit,
        ),
    }