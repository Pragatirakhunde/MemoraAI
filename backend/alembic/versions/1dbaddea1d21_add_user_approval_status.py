"""add user approval status

Revision ID: 1dbaddea1d21
Revises: 7d5bf064615d
Create Date: ...
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "1dbaddea1d21"
down_revision: Union[str, Sequence[str], None] = "7d5bf064615d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "approval_status",
            sa.String(length=20),
            nullable=True,
        ),
    )

    op.execute(
        "UPDATE users "
        "SET approval_status = 'APPROVED' "
        "WHERE approval_status IS NULL"
    )

    op.alter_column(
        "users",
        "approval_status",
        existing_type=sa.String(length=20),
        nullable=False,
    )

    op.create_check_constraint(
        "check_user_approval_status",
        "users",
        "approval_status IN ('PENDING', 'APPROVED', 'REJECTED')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "check_user_approval_status",
        "users",
        type_="check",
    )

    op.drop_column(
        "users",
        "approval_status",
    )