from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class CodeCommit(Base):
    __tablename__ = "code_commits"

    __table_args__ = (
        UniqueConstraint("repository_id", "sha", name="uq_code_commit_repository_sha"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    organization_id: Mapped[int] = mapped_column(
        ForeignKey("organizations.id"), nullable=False, index=True
    )
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id"), nullable=False, index=True
    )
    repository_id: Mapped[int] = mapped_column(
        ForeignKey("code_repositories.id"), nullable=False, index=True
    )
    sha: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    author_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    author_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    committed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    changed_files: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    additions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    deletions: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
