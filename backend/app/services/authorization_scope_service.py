from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)
from app.repositories.project_repository import (
    ProjectRepository,
)


@dataclass(frozen=True)
class AuthorizationScope:
    organization_id: int
    project_ids: list[int]
    project_names: list[str]


class AuthorizationScopeService:

    @staticmethod
    def get_scope(
        db: Session,
        current_user: User,
    ) -> AuthorizationScope:

        if current_user.role == "admin":

            projects = (
                ProjectRepository.get_all_by_org(
                    db=db,
                    organization_id=current_user.organization_id,
                )
            )

        else:

            projects = (
                ProjectMemberRepository.get_projects_for_user(
                    db=db,
                    user_id=current_user.id,
                    organization_id=current_user.organization_id,
                )
            )

        return AuthorizationScope(
            organization_id=current_user.organization_id,
            project_ids=[
                project.id
                for project in projects
            ],
            project_names=[
                project.name
                for project in projects
            ],
        )