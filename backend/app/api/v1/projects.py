from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
)
from sqlalchemy.orm import Session
from app.database.postgres import get_db
from app.models.user import User
from app.schemas.project import (
    ProjectCreate,
    ProjectResponse,
)

from app.schemas.project_member import (
    ProjectMemberCreate,
    ProjectMemberResponse,
)
from app.api.v1.auth.roles import (
    require_admin,
    require_employee,
)
from app.services.project_service import ProjectService
from app.api.v1.auth.authorization import require_project_access
from app.models.project import Project


router = APIRouter(
    prefix="/projects",
    tags=["Projects"],
)


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_project(
    data: ProjectCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    try:
        return ProjectService.create_project(
            db=db,
            organization_id=current_user.organization_id,
            name=data.name,
            slug=data.slug,
            description=data.description,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )


@router.get(
    "",
    response_model=list[ProjectResponse],
)
def get_projects(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    return ProjectService.get_projects(
        db=db,
        organization_id=current_user.organization_id,
    )

@router.post(
    "/{project_id}/members",
    response_model=ProjectMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def assign_project_member(
    project_id: int,
    data: ProjectMemberCreate,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    try:
        return ProjectService.assign_member(
            db=db,
            organization_id=current_user.organization_id,
            project_id=project_id,
            user_id=data.user_id,
            permission=data.permission,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(exc),
        )

@router.get(
    "/{project_id}/members",
    response_model=list[ProjectMemberResponse],
)
def get_project_members(
    project_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    project, members = ProjectService.get_members(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return members

@router.delete(
    "/{project_id}/members/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def remove_project_member(
    project_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):

    result = ProjectService.remove_member(
        db=db,
        organization_id=current_user.organization_id,
        project_id=project_id,
        user_id=user_id,
    )

    if result is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if result is False:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project member not found",
        )

    return None

@router.get(
    "/my",
    response_model=list[ProjectResponse],
)
def get_my_projects(
    db: Session = Depends(get_db),
    current_user=Depends(require_employee),
):

    return ProjectService.get_my_projects(
        db=db,
        user_id=current_user.id,
        organization_id=current_user.organization_id,
    )


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
)
def get_project(
    project_id: int,
    project: Project = Depends(require_project_access),
):
    return project


@router.patch(
    "/{project_id}/archive",
    response_model=ProjectResponse,
)
def archive_project(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):

    project = ProjectService.archive_project(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project