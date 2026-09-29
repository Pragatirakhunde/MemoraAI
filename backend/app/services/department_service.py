from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department
from app.repositories.department_repository import (
    DepartmentRepository,
)


class DepartmentService:

    @staticmethod
    def create_department(
        db: Session,
        organization_id: int,
        name: str,
        description: str | None = None,
    ):

        existing = db.scalar(
            select(Department).where(
                Department.organization_id == organization_id,
                Department.name == name.strip(),
            )
        )

        if existing is not None:
            raise ValueError(
                "Department already exists in this organization."
            )

        return DepartmentRepository.create(
            db=db,
            organization_id=organization_id,
            name=name,
            description=description,
        )

    @staticmethod
    def get_departments(
        db: Session,
        organization_id: int,
    ):

        return DepartmentRepository.get_all_by_org(
            db,
            organization_id,
        )