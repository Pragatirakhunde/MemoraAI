from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:

    @staticmethod
    def get_by_email(
        db: Session,
        email: str,
    ) -> User | None:
        statement = select(User).where(
            User.email == email
        )
        return db.scalar(statement)

    @staticmethod
    def get_by_id(
        db: Session,
        user_id: int,
    ) -> User | None:
        return db.get(User, user_id)

    @staticmethod
    def get_by_id_and_org(
        db: Session,
        user_id: int,
        organization_id: int,
    ) -> User | None:
        statement = select(User).where(
            User.id == user_id,
            User.organization_id == organization_id,
        )
        return db.scalar(statement)

    @staticmethod
    def get_all_by_org(
        db: Session,
        organization_id: int,
    ) -> list[User]:
        statement = (
            select(User)
            .where(User.organization_id == organization_id)
            .order_by(User.id)
        )
        return list(db.scalars(statement).all())

    @staticmethod
    def create(
        db: Session,
        organization_id: int,
        name: str,
        email: str,
        password_hash: str,
        role: str = "employee",
        approval_status: str = "APPROVED",
        is_active: bool = True,
    ) -> User:

        user = User(
            organization_id=organization_id,
            name=name,
            email=email,
            password_hash=password_hash,
            role=role,
            approval_status=approval_status,
            is_active=is_active,
        )

        db.add(user)
        db.commit()
        db.refresh(user)

        return user

    @staticmethod
    def get_pending_by_org(
        db: Session,
        organization_id: int,
    ) -> list[User]:
        statement = (
            select(User)
            .where(
                User.organization_id == organization_id,
                User.approval_status == "PENDING",
            )
            .order_by(User.created_at)
        )

        return list(db.scalars(statement).all())