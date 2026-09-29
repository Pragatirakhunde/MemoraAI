from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.postgres import Base


class CodeSymbol(Base):
    __tablename__ = "code_symbols"

    __table_args__ = (
        UniqueConstraint(
            "file_id",
            "qualified_name",
            "start_line",
            name="uq_code_symbol_location",
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
    parent_symbol_id: Mapped[int | None] = mapped_column(
        ForeignKey("code_symbols.id"), nullable=True, index=True
    )
    symbol_type: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(300), nullable=False, index=True)
    qualified_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    docstring: Mapped[str | None] = mapped_column(Text, nullable=True)
    start_line: Mapped[int] = mapped_column(Integer, nullable=False)
    end_line: Mapped[int] = mapped_column(Integer, nullable=False)
    metadata_json: Mapped[dict] = mapped_column("metadata", JSON, default=dict, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
