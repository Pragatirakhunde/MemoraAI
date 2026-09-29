"""Phase 16 CodeMind symbols, chunks and commits."""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "9d0b2c6e5a10"
down_revision: Union[str, Sequence[str], None] = "811a53cca653"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("code_repositories", sa.Column("index_status", sa.String(length=20), nullable=False, server_default="never"))
    op.add_column("code_repositories", sa.Column("last_indexed_at", sa.DateTime(), nullable=True))
    op.add_column("code_repositories", sa.Column("last_index_error", sa.Text(), nullable=True))
    op.create_check_constraint("check_code_repository_index_status", "code_repositories", "index_status IN ('never','pending','running','completed','failed')")
    op.alter_column("code_repositories", "index_status", server_default=None)
    op.add_column("code_files", sa.Column("analysis", sa.JSON(), nullable=False, server_default="{}"))
    op.alter_column("code_files", "analysis", server_default=None)

    op.create_table(
        "code_symbols",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("parent_symbol_id", sa.Integer(), nullable=True),
        sa.Column("symbol_type", sa.String(length=40), nullable=False),
        sa.Column("name", sa.String(length=300), nullable=False),
        sa.Column("qualified_name", sa.String(length=1000), nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("docstring", sa.Text(), nullable=True),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("metadata", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["repository_id"], ["code_repositories.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["code_files.id"]),
        sa.ForeignKeyConstraint(["parent_symbol_id"], ["code_symbols.id"]),
        sa.UniqueConstraint("file_id", "qualified_name", "start_line", name="uq_code_symbol_location"),
    )
    for name, cols in [
        ("ix_code_symbols_id", ["id"]), ("ix_code_symbols_organization_id", ["organization_id"]),
        ("ix_code_symbols_project_id", ["project_id"]), ("ix_code_symbols_repository_id", ["repository_id"]),
        ("ix_code_symbols_file_id", ["file_id"]), ("ix_code_symbols_parent_symbol_id", ["parent_symbol_id"]),
        ("ix_code_symbols_symbol_type", ["symbol_type"]), ("ix_code_symbols_name", ["name"]),
    ]:
        op.create_index(name, "code_symbols", cols)

    op.create_table(
        "code_chunks",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("symbol_id", sa.Integer(), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("start_line", sa.Integer(), nullable=False),
        sa.Column("end_line", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint("status IN ('active','deleted')", name="check_code_chunk_status"),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["repository_id"], ["code_repositories.id"]),
        sa.ForeignKeyConstraint(["file_id"], ["code_files.id"]),
        sa.ForeignKeyConstraint(["symbol_id"], ["code_symbols.id"]),
        sa.UniqueConstraint("file_id", "chunk_index", name="uq_code_chunk_file_index"),
    )
    for name, cols in [
        ("ix_code_chunks_id", ["id"]), ("ix_code_chunks_organization_id", ["organization_id"]),
        ("ix_code_chunks_project_id", ["project_id"]), ("ix_code_chunks_repository_id", ["repository_id"]),
        ("ix_code_chunks_file_id", ["file_id"]), ("ix_code_chunks_symbol_id", ["symbol_id"]),
    ]:
        op.create_index(name, "code_chunks", cols)

    op.create_table(
        "code_commits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("organization_id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("repository_id", sa.Integer(), nullable=False),
        sa.Column("sha", sa.String(length=80), nullable=False),
        sa.Column("author_name", sa.String(length=300), nullable=True),
        sa.Column("author_email", sa.String(length=320), nullable=True),
        sa.Column("committed_at", sa.DateTime(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("changed_files", sa.JSON(), nullable=False),
        sa.Column("additions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("deletions", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"]),
        sa.ForeignKeyConstraint(["repository_id"], ["code_repositories.id"]),
        sa.UniqueConstraint("repository_id", "sha", name="uq_code_commit_repository_sha"),
    )
    for name, cols in [
        ("ix_code_commits_id", ["id"]), ("ix_code_commits_organization_id", ["organization_id"]),
        ("ix_code_commits_project_id", ["project_id"]), ("ix_code_commits_repository_id", ["repository_id"]),
        ("ix_code_commits_sha", ["sha"]),
    ]:
        op.create_index(name, "code_commits", cols)


def downgrade() -> None:
    for name in ["ix_code_commits_sha","ix_code_commits_repository_id","ix_code_commits_project_id","ix_code_commits_organization_id","ix_code_commits_id"]:
        op.drop_index(name, table_name="code_commits")
    op.drop_table("code_commits")
    for name in ["ix_code_chunks_symbol_id","ix_code_chunks_file_id","ix_code_chunks_repository_id","ix_code_chunks_project_id","ix_code_chunks_organization_id","ix_code_chunks_id"]:
        op.drop_index(name, table_name="code_chunks")
    op.drop_table("code_chunks")
    for name in ["ix_code_symbols_name","ix_code_symbols_symbol_type","ix_code_symbols_parent_symbol_id","ix_code_symbols_file_id","ix_code_symbols_repository_id","ix_code_symbols_project_id","ix_code_symbols_organization_id","ix_code_symbols_id"]:
        op.drop_index(name, table_name="code_symbols")
    op.drop_table("code_symbols")
    op.drop_column("code_files", "analysis")
    op.drop_constraint("check_code_repository_index_status", "code_repositories", type_="check")
    op.drop_column("code_repositories", "last_index_error")
    op.drop_column("code_repositories", "last_indexed_at")
    op.drop_column("code_repositories", "index_status")
