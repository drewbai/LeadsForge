"""create lead assignment history table

Revision ID: 0021_create_lead_assignment_history
Revises: 0020_create_lead_assignment
Create Date: 2026-05-08 19:10:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0021_create_lead_assignment_history"
down_revision: Union[str, None] = "0020_create_lead_assignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_assignment_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_assigned_to", sa.Text(), nullable=True),
        sa.Column("new_assigned_to", sa.Text(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.Text(), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_assignment_history_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_assignment_history_lead_id",
        "lead_assignment_history",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_assignment_history_new_assigned_to",
        "lead_assignment_history",
        ["new_assigned_to"],
        unique=False,
    )
    op.create_index(
        "ix_lead_assignment_history_changed_at",
        "lead_assignment_history",
        ["changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_assignment_history_changed_at",
        table_name="lead_assignment_history",
    )
    op.drop_index(
        "ix_lead_assignment_history_new_assigned_to",
        table_name="lead_assignment_history",
    )
    op.drop_index(
        "ix_lead_assignment_history_lead_id",
        table_name="lead_assignment_history",
    )
    op.drop_table("lead_assignment_history")
