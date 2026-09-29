from urllib.parse import unquote

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
)
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_employee
from app.database.postgres import get_db
from app.models.user import User

from app.schemas.graph import (
    GraphDatabaseResponse,
    GraphNeighborhoodResponse,
    GraphProjectResponse,
    ProjectContextResponse,
    ProjectKnowledgeResponse,
)

from app.services.authorization_scope_service import (
    AuthorizationScopeService,
)

from app.services.graph_query_service import (
    GraphQueryService,
)


router = APIRouter(
    prefix="/graph",
    tags=["Knowledge Graph"],
)


# =========================================================
# PROJECTS
# =========================================================

@router.get("/projects")
def list_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return GraphQueryService.list_projects(
        organization_id=scope.organization_id,
        project_ids=scope.project_ids,
    )


@router.get(
    "/projects/{project_name}",
    response_model=ProjectContextResponse,
)
def get_project_context(
    project_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(project_name)

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    result = GraphQueryService.get_project_context(
        organization_id=scope.organization_id,
        project_name=project_name,
        project_ids=scope.project_ids,
    )

    if result["project"] is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result


# =========================================================
# TECHNOLOGY
# =========================================================

@router.get(
    "/technologies/{technology_name}/projects",
    response_model=list[GraphProjectResponse],
)
def get_projects_using_technology(
    technology_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    technology_name = unquote(
        technology_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return (
        GraphQueryService
        .get_projects_using_technology(
            organization_id=scope.organization_id,
            technology_name=technology_name,
            project_ids=scope.project_ids,
        )
    )


# =========================================================
# DATABASE
# =========================================================

@router.get(
    "/databases/{database_name}/projects",
    response_model=list[GraphDatabaseResponse],
)
def get_projects_using_database(
    database_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    database_name = unquote(
        database_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return (
        GraphQueryService
        .get_projects_using_database(
            organization_id=scope.organization_id,
            database_name=database_name,
            project_ids=scope.project_ids,
        )
    )


# =========================================================
# ENTITY -> DOCUMENTS
# =========================================================

@router.get(
    "/entities/{entity_name}/documents",
)
def get_entity_documents(
    entity_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(entity_name)

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return (
        GraphQueryService
        .get_documents_for_entity(
            organization_id=scope.organization_id,
            entity_name=entity_name,
            project_ids=scope.project_ids,
        )
    )


# =========================================================
# PROJECT KNOWLEDGE
# =========================================================

@router.get(
    "/projects/{project_name}/knowledge",
    response_model=ProjectKnowledgeResponse,
)
def get_project_knowledge(
    project_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(
        project_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    result = (
        GraphQueryService
        .get_project_knowledge(
            organization_id=scope.organization_id,
            project_name=project_name,
            project_ids=scope.project_ids,
        )
    )

    if result["project"] is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result


# =========================================================
# ENTITY NEIGHBORHOOD
# =========================================================

@router.get(
    "/entities/{entity_name}/neighborhood",
    response_model=list[
        GraphNeighborhoodResponse
    ],
)
def get_entity_neighborhood(
    entity_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(entity_name)

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return (
        GraphQueryService
        .get_entity_neighborhood(
            organization_id=scope.organization_id,
            entity_name=entity_name,
            project_ids=scope.project_ids,
        )
    )


# =========================================================
# PROJECT GRAPH
# =========================================================

@router.get(
    "/project/{project_name}/graph"
)
def get_project_graph(
    project_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(
        project_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    result = (
        GraphQueryService
        .get_project_graph(
            organization_id=scope.organization_id,
            project_name=project_name,
            project_ids=scope.project_ids,
        )
    )

    if not result["nodes"]:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result


# =========================================================
# PROJECT
# =========================================================

@router.get(
    "/project/{project_name}"
)
def get_project(
    project_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    project_name = unquote(
        project_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    result = (
        GraphQueryService
        .get_project_context(
            organization_id=scope.organization_id,
            project_name=project_name,
            project_ids=scope.project_ids,
        )
    )

    if result["project"] is None:
        raise HTTPException(
            status_code=404,
            detail="Project not found.",
        )

    return result


# =========================================================
# ENTITY
# =========================================================

@router.get(
    "/entity/{entity_name}"
)
def get_entity(
    entity_name: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(
        entity_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return {
        "entity": entity_name,
        "relationships": (
            GraphQueryService
            .get_entity_neighborhood(
                organization_id=(
                    scope.organization_id
                ),
                entity_name=entity_name,
                project_ids=scope.project_ids,
            )
        ),
    }


# =========================================================
# ENTITY EXPANSION
# =========================================================

@router.get(
    "/entity/{entity_name}/expand"
)
def expand_entity(
    entity_name: str,
    max_hops: int = 2,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    entity_name = unquote(
        entity_name
    )

    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return {
        "entity": entity_name,
        "max_hops": max_hops,
        "results": (
            GraphQueryService
            .expand_entity(
                organization_id=(
                    scope.organization_id
                ),
                entity_name=entity_name,
                project_ids=scope.project_ids,
                max_hops=max_hops,
                limit=limit,
            )
        ),
    }


# =========================================================
# GRAPH STATS
# =========================================================

@router.get("/stats")
def get_graph_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(
        require_employee
    ),
):
    scope = AuthorizationScopeService.get_scope(
        db=db,
        current_user=current_user,
    )

    return (
        GraphQueryService
        .get_graph_stats(
            organization_id=scope.organization_id,
            project_ids=scope.project_ids,
        )
    )