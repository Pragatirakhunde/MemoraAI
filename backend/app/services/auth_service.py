from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.repositories.user_repository import UserRepository
from app.models.user import User


class AuthService:

    @staticmethod
    def login(
        db: Session,
        email: str,
        password: str,
    ):
        user = UserRepository.get_by_email(
            db,
            email,
        )

        if user is None:
            return None

        if not user.is_active:
            return None

        if not verify_password(
            password,
            user.password_hash,
        ):
            return None

        token = create_access_token(
            user_id=user.id,
            role=user.role,
            organization_id=user.organization_id,
        )

        return token

    @staticmethod
    def register(
        db: Session,
        name: str,
        email: str,
        password: str,
    ):
        existing_user = UserRepository.get_by_email(
            db,
            email,
        )

        if existing_user is not None:
            return None

        user = User(
            organization_id=1,
            name=name.strip(),
            email=email.lower().strip(),
            password_hash=hash_password(password),
            role="employee",
            approval_status="PENDING",
            is_active=False,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_user(
        db: Session,
        user_id: int,
    ):
        return UserRepository.get_by_id(
            db,
            user_id,
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
    def assign_department(
        db: Session,
        user_id: int,
        organization_id: int,
        department_id: int,
    ):

        user = UserRepository.get_by_id_and_org(
            db,
            user_id,
            organization_id,
        )

        if user is None:
            return None

        from app.repositories.department_repository import (
            DepartmentRepository,
        )

        department = DepartmentRepository.get_by_id_and_org(
            db,
            department_id,
            organization_id,
        )

        if department is None:
            raise ValueError(
                "Department not found in this organization."
            )

        user.department_id = department.id

        db.commit()
        db.refresh(user)

        return user