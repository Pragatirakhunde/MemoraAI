from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project_member import ProjectMember


class ProjectMemberRepository:

    @staticmethod
    def get_by_project_and_user(
        db: Session,
        project_id: int,
        user_id: int,
    ) -> ProjectMember | None:

        statement = select(ProjectMember).where(
            ProjectMember.project_id == project_id,
            ProjectMember.user_id == user_id,
        )

        return db.scalar(statement)

    @staticmethod
    def create(
        db: Session,
        project_id: int,
        user_id: int,
        permission: str,
    ) -> ProjectMember:

        member = ProjectMember(
            project_id=project_id,
            user_id=user_id,
            permission=permission,
        )

        db.add(member)
        db.commit()
        db.refresh(member)

        return member

    @staticmethod
    def get_by_project(
        db: Session,
        project_id: int,
    ) -> list[ProjectMember]:

        statement = (
            select(ProjectMember)
            .where(
                ProjectMember.project_id == project_id
            )
            .order_by(ProjectMember.created_at)
        )

        return list(db.scalars(statement).all())

    @staticmethod
    def delete(
        db: Session,
        member: ProjectMember,
    ) -> None:

        db.delete(member)
        db.commit()

    @staticmethod
    def get_projects_for_user(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        from app.models.project import Project

        statement = (
            select(Project)
            .join(
                ProjectMember,
                ProjectMember.project_id == Project.id,
            )
            .where(
                ProjectMember.user_id == user_id,
                Project.organization_id == organization_id,
                Project.status == "active",
            )
            .order_by(Project.name)
        )

        return list(db.scalars(statement).all())