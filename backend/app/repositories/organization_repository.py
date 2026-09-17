from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.organization import Organization


class OrganizationRepository:

    @staticmethod
    def create(
        db: Session,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> Organization:

        organization = Organization(
            name=name,
            slug=slug,
            description=description,
        )

        db.add(organization)
        db.commit()
        db.refresh(organization)

        return organization

    @staticmethod
    def get_by_id(
        db: Session,
        organization_id: int,
    ) -> Organization | None:

        return db.get(Organization, organization_id)

    @staticmethod
    def get_by_slug(
        db: Session,
        slug: str,
    ) -> Organization | None:

        stmt = select(Organization).where(
            Organization.slug == slug
        )

        return db.scalar(stmt)

    @staticmethod
    def get_all(
        db: Session,
    ) -> list[Organization]:

        stmt = select(Organization).order_by(
            Organization.id
        )

        return list(db.scalars(stmt).all())