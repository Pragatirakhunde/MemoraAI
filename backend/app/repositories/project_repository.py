from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import Project


class ProjectRepository:

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> Project:

        project = Project(
            organization_id=organization_id,
            name=name.strip(),
            slug=slug.strip().lower(),
            description=description,
            status="active",
        )

        db.add(project)
        db.commit()
        db.refresh(project)

        return project

    @staticmethod
    def get_by_id_and_org(
        db: Session,
        project_id: int,
        organization_id: int,
    ) -> Project | None:

        statement = select(Project).where(
            Project.id == project_id,
            Project.organization_id == organization_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_by_slug_and_org(
        db: Session,
        slug: str,
        organization_id: int,
    ) -> Project | None:

        statement = select(Project).where(
            Project.slug == slug.strip().lower(),
            Project.organization_id == organization_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all_by_org(
        db: Session,
        organization_id: int,
    ) -> list[Project]:

        statement = (
            select(Project)
            .where(
                Project.organization_id == organization_id
            )
            .order_by(Project.name)
        )

        return list(db.scalars(statement).all())