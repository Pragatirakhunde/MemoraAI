from sqlalchemy.orm import Session

from app.repositories.organization_repository import OrganizationRepository
from app.schemas.organization import OrganizationCreate


class OrganizationService:

    @staticmethod
    def create_organization(
        db: Session,
        data: OrganizationCreate,
    ):
        existing = OrganizationRepository.get_by_slug(
            db,
            data.slug,
        )

        if existing:
            raise ValueError("Organization slug already exists")

        return OrganizationRepository.create(
            db=db,
            name=data.name,
            slug=data.slug,
            description=data.description,
        )

    @staticmethod
    def get_organization(
        db: Session,
        organization_id: int,
    ):
        return OrganizationRepository.get_by_id(
            db,
            organization_id,
        )

    @staticmethod
    def get_all_organizations(
        db: Session,
    ):
        return OrganizationRepository.get_all(db)