from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.repositories.department_repository import (
    DepartmentRepository,
)
from app.repositories.user_repository import UserRepository
from app.schemas.user import UserCreate


class UserService:

    @staticmethod
    def create_employee(
        db: Session,
        organization_id: int,
        data: UserCreate,
    ):
        existing = UserRepository.get_by_email(
            db,
            data.email,
        )

        if existing:
            raise ValueError("Email already registered")

        return UserRepository.create(
            db=db,
            organization_id=organization_id,
            name=data.name,
            email=data.email,
            password_hash=hash_password(data.password),
            role="employee",
            approval_status="APPROVED",
            is_active=True,
        )

    @staticmethod
    def get_users(
        db: Session,
        organization_id: int,
    ):
        return UserRepository.get_all_by_org(
            db,
            organization_id,
        )

    @staticmethod
    def get_pending_users(
        db: Session,
        organization_id: int,
    ):
        return UserRepository.get_pending_by_org(
            db,
            organization_id,
        )

    @staticmethod
    def approve_user(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            return None

        if user.role != "employee":
            raise ValueError(
                "Only employee accounts can be approved."
            )

        if user.approval_status != "PENDING":
            raise ValueError(
                "Only pending users can be approved."
            )

        user.approval_status = "APPROVED"
        user.is_active = True

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def reject_user(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            return None

        if user.role != "employee":
            raise ValueError(
                "Only employee accounts can be rejected."
            )

        if user.approval_status != "PENDING":
            raise ValueError(
                "Only pending users can be rejected."
            )

        user.approval_status = "REJECTED"
        user.is_active = False

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        return UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

    @staticmethod
    def deactivate_user(
        db: Session,
        user_id: int,
        organization_id: int,
    ):
        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            return None

        user.is_active = False

        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def assign_department(
        db: Session,
        user_id: int,
        organization_id: int,
        department_id: int | None,
    ):
        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            return None

        if department_id is not None:
            department = (
                DepartmentRepository.get_by_id_and_org(
                    db,
                    department_id,
                    organization_id,
                )
            )

            if department is None:
                raise ValueError(
                    "Department not found."
                )

        user.department_id = department_id

        db.commit()
        db.refresh(user)

        return user