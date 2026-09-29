from sqlalchemy.orm import Session

from app.repositories.project_repository import (
    ProjectRepository,
)
from app.models.user import User
from app.repositories.project_member_repository import (
    ProjectMemberRepository,
)
from app.repositories.user_repository import UserRepository


class ProjectService:

    @staticmethod
    def create_project(
        db: Session,
        organization_id: int,
        name: str,
        slug: str,
        description: str | None = None,
    ):

        normalized_slug = slug.strip().lower()

        existing = ProjectRepository.get_by_slug_and_org(
            db,
            normalized_slug,
            organization_id,
        )

        if existing is not None:
            raise ValueError(
                "Project slug already exists in this organization."
            )

        return ProjectRepository.create(
            db=db,
            organization_id=organization_id,
            name=name,
            slug=normalized_slug,
            description=description,
        )

    @staticmethod
    def get_projects(
        db: Session,
        organization_id: int,
    ):

        return ProjectRepository.get_all_by_org(
            db,
            organization_id,
        )

    @staticmethod
    def get_project(
        db: Session,
        project_id: int,
        organization_id: int,
    ):

        return ProjectRepository.get_by_id_and_org(
            db,
            project_id,
            organization_id,
        )

    @staticmethod
    def archive_project(
        db: Session,
        project_id: int,
        organization_id: int,
    ):

        project = ProjectRepository.get_by_id_and_org(
            db,
            project_id,
            organization_id,
        )

        if project is None:
            return None

        project.status = "archived"

        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def assign_member(
        db: Session,
        organization_id: int,
        project_id: int,
        user_id: int,
        permission: str,
    ):

        project = ProjectRepository.get_by_id_and_org(
            db,
            project_id,
            organization_id,
        )

        if project is None:
            raise ValueError("Project not found.")

        if project.status != "active":
            raise ValueError(
                "Archived projects cannot receive new members."
            )

        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            raise ValueError("User not found.")

        if user.role != "employee":
            raise ValueError(
                "Only employees can be assigned to projects."
            )

        if user.approval_status != "APPROVED":
            raise ValueError(
                "User must be approved before project assignment."
            )

        if not user.is_active:
            raise ValueError(
                "Inactive users cannot be assigned to projects."
            )

        existing = (
            ProjectMemberRepository.get_by_project_and_user(
                db,
                project_id,
                user_id,
            )
        )

        if existing is not None:
            raise ValueError(
                "User is already assigned to this project."
            )

        return ProjectMemberRepository.create(
            db=db,
            project_id=project_id,
            user_id=user_id,
            permission=permission,
        )

    @staticmethod
    def get_members(
        db: Session,
        organization_id: int,
        project_id: int,
    ):

        project = ProjectRepository.get_by_id_and_org(
            db,
            project_id,
            organization_id,
        )

        if project is None:
            return None, []

        return (
            project,
            ProjectMemberRepository.get_by_project(
                db,
                project_id,
            ),
        )

    @staticmethod
    def remove_member(
        db: Session,
        organization_id: int,
        project_id: int,
        user_id: int,
    ):

        project = ProjectRepository.get_by_id_and_org(
            db,
            project_id,
            organization_id,
        )

        if project is None:
            return None

        member = (
            ProjectMemberRepository.get_by_project_and_user(
                db,
                project_id,
                user_id,
            )
        )

        if member is None:
            return False

        ProjectMemberRepository.delete(
            db,
            member,
        )

        return True

    @staticmethod
    def get_my_projects(
        db: Session,
        user_id: int,
        organization_id: int,
    ):

        return ProjectMemberRepository.get_projects_for_user(
            db,
            user_id,
            organization_id,
        )