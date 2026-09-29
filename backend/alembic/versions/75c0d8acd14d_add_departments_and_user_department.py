"""add departments and user department

Revision ID: 75c0d8acd14d
Revises: 1dbaddea1d21
Create Date: <keep generated date>
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "75c0d8acd14d"
down_revision: Union[str, Sequence[str], None] = "1dbaddea1d21"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "departments",
        sa.Column(
            "id",
            sa.Integer(),
            primary_key=True,
            index=True,
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
            "description",
            sa.Text(),
            nullable=True,
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
            name="fk_departments_organization_id",
        ),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_department_organization_name",
        ),
    )

    op.create_index(
        "ix_departments_organization_id",
        "departments",
        ["organization_id"],
    )

    op.add_column(
        "users",
        sa.Column(
            "department_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_index(
        "ix_users_department_id",
        "users",
        ["department_id"],
    )

    op.create_foreign_key(
        "fk_users_department_id",
        "users",
        "departments",
        ["department_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_users_department_id",
        "users",
        type_="foreignkey",
    )

    op.drop_index(
        "ix_users_department_id",
        table_name="users",
    )

    op.drop_column(
        "users",
        "department_id",
    )

    op.drop_index(
        "ix_departments_organization_id",
        table_name="departments",
    )

    op.drop_constraint(
        "uq_department_organization_name",
        "departments",
        type_="unique",
    )

    op.drop_constraint(
        "fk_departments_organization_id",
        "departments",
        type_="foreignkey",
    )

    op.drop_table("departments")