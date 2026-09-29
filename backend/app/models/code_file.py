from datetime import datetime

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    String,
    JSON,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class CodeFile(Base):
    __tablename__ = "code_files"

    __table_args__ = (
        UniqueConstraint(
            "repository_id",
            "file_path",
            name="uq_code_file_repository_path",
        ),
        CheckConstraint(
            "status IN ('active', 'deleted')",
            name="check_code_file_status",
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

    repository_id: Mapped[int] = mapped_column(
        ForeignKey("code_repositories.id"),
        nullable=False,
        index=True,
    )

    file_path: Mapped[str] = mapped_column(
        String(1500),
        nullable=False,
    )

    file_name: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    extension: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    language: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    size_bytes: Mapped[int] = mapped_column(
        nullable=False,
        default=0,
    )

    checksum: Mapped[str] = mapped_column(
        String(64),
        nullable=False,
    )

    analysis_json: Mapped[dict] = mapped_column(
        "analysis", JSON, default=dict, nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="active",
    )

    last_indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )