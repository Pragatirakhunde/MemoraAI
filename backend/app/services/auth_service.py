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
            is_active=True,
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