"""add projects and project members

Revision ID: 5364dbc052af
Revises: 75c0d8acd14d
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "5364dbc052af"
down_revision: Union[str, Sequence[str], None] = "75c0d8acd14d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "projects",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "slug",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            name="fk_projects_organization_id",
        ),
        sa.UniqueConstraint(
            "organization_id",
            "slug",
            name="uq_project_organization_slug",
        ),
        sa.CheckConstraint(
            "status IN ('active', 'archived')",
            name="check_project_status",
        ),
    )

    op.create_index(
        "ix_projects_organization_id",
        "projects",
        ["organization_id"],
    )

    op.create_table(
        "project_members",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            nullable=False,
        ),
        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "permission",
            sa.String(length=30),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_project_members_project_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_project_members_user_id",
        ),
        sa.UniqueConstraint(
            "project_id",
            "user_id",
            name="uq_project_member",
        ),
        sa.CheckConstraint(
            "permission IN ('PROJECT_MEMBER', 'PROJECT_VIEWER')",
            name="check_project_member_permission",
        ),
    )

    op.create_index(
        "ix_project_members_project_id",
        "project_members",
        ["project_id"],
    )

    op.create_index(
        "ix_project_members_user_id",
        "project_members",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_project_members_user_id",
        table_name="project_members",
    )

    op.drop_index(
        "ix_project_members_project_id",
        table_name="project_members",
    )

    op.drop_constraint(
        "check_project_member_permission",
        "project_members",
        type_="check",
    )

    op.drop_constraint(
        "uq_project_member",
        "project_members",
        type_="unique",
    )

    op.drop_constraint(
        "fk_project_members_user_id",
        "project_members",
        type_="foreignkey",
    )

    op.drop_constraint(
        "fk_project_members_project_id",
        "project_members",
        type_="foreignkey",
    )

    op.drop_table("project_members")

    op.drop_index(
        "ix_projects_organization_id",
        table_name="projects",
    )

    op.drop_constraint(
        "check_project_status",
        "projects",
        type_="check",
    )

    op.drop_constraint(
        "uq_project_organization_slug",
        "projects",
        type_="unique",
    )

    op.drop_constraint(
        "fk_projects_organization_id",
        "projects",
        type_="foreignkey",
    )

    op.drop_table("projects")