from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    verify_password,
)
from app.repositories.user_repository import UserRepository


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
    def get_user(
        db: Session,
        user_id: int,
    ):
        return UserRepository.get_by_id(
            db,
            user_id,
        )