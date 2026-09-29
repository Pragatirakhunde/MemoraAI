from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class CodeRepository(Base):
    __tablename__ = "code_repositories"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "project_id",
            "name",
            name="uq_code_repository_project_name",
        ),
        CheckConstraint(
            "provider IN ('local', 'github')",
            name="check_code_repository_provider",
        ),
        CheckConstraint(
            "status IN ('active', 'archived')",
            name="check_code_repository_status",
        ),
        CheckConstraint(
            "index_status IN ('never', 'pending', 'running', 'completed', 'failed')",
            name="check_code_repository_index_status",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"),
        nullable=False,
        index=True,
    )

    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"),
        nullable=False,
        index=True,
    )

    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )

    provider: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="local",
    )

    remote_url: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    local_path: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    default_branch: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
        default="main",
    )

    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    index_status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="never"
    )

    last_indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )

    last_index_error: Mapped[str | None] = mapped_column(
        Text, nullable=True
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )