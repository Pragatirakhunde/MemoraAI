from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.v1.auth.roles import require_employee
from app.database.postgres import get_db
from app.models.project import Project
from app.models.user import User
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)
from app.repositories.project_repository import (
    ProjectRepository,
)


def require_project_access(
    project_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_employee),
) -> Project:

    project = ProjectRepository.get_by_id_and_org(
        db=db,
        project_id=project_id,
        organization_id=current_user.organization_id,
    )

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Admin has organization-wide project management/access.
    if current_user.role == "admin":
        return project

    # Employees must have explicit membership.
    membership = (
        ProjectMemberRepository.get_by_project_and_user(
            db=db,
            project_id=project_id,
            user_id=current_user.id,
        )
    )

    if membership is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Project access denied",
        )

    # Archived projects are not available to normal employees.
    if project.status != "active":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    return project