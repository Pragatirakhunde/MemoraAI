from sqlalchemy.orm import Session

from app.core.security import hash_password
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