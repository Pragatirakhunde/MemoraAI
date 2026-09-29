from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.department import Department


class DepartmentRepository:

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        name: str,
        description: str | None = None,
    ) -> Department:

        department = Department(
            organization_id=organization_id,
            name=name.strip(),
            description=description,
        )

        db.add(department)
        db.commit()
        db.refresh(department)

        return department

    @staticmethod
    def get_by_id_and_org(
        db: Session,
        department_id: int,
        organization_id: int,
    ) -> Department | None:

        statement = select(Department).where(
            Department.id == department_id,
            Department.organization_id == organization_id,
        )

        return db.scalar(statement)

    @staticmethod
    def get_all_by_org(
        db: Session,
        organization_id: int,
    ) -> list[Department]:

        statement = (
            select(Department)
            .where(
                Department.organization_id == organization_id
            )
            .order_by(Department.name)
        )

        return list(db.scalars(statement).all())