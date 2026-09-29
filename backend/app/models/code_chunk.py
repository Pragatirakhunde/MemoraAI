from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class CodeChunk(Base):
    __tablename__ = "code_chunks"

    __table_args__ = (
        UniqueConstraint("file_id", "chunk_index", name="uq_code_chunk_file_index"),
        CheckConstraint(
            "status IN ('active', 'deleted')",
            name="check_code_chunk_status",
        ),
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
    file_id: Mapped[int] = mapped_column(
        ForeignKey("code_files.id"), nullable=False, index=True
    )
    symbol_id: Mapped[int | None] = mapped_column(
        ForeignKey("code_symbols.id"), nullable=True, index=True
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    checksum: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="active", nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
