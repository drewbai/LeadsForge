"""create lead task assignment table

Revision ID: 0043_create_lead_task_assignment
Revises: 0042_create_lead_task_history
Create Date: 2026-05-08 19:58:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0043_create_lead_task_assignment"
down_revision: Union[str, None] = "0042_create_lead_task_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_task_assignment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", sa.Text(), nullable=False),
        sa.Column("assigned_by", sa.Text(), nullable=True),
        sa.Column("assignment_reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["lead_task.id"],
            name="fk_lead_task_assignment_task_id_lead_task",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_task_assignment_task_id", "lead_task_assignment", ["task_id"], unique=False)
    op.create_index("ix_lead_task_assignment_assigned_to", "lead_task_assignment", ["assigned_to"], unique=False)
    op.create_index("ix_lead_task_assignment_assigned_by", "lead_task_assignment", ["assigned_by"], unique=False)
    op.create_index("ix_lead_task_assignment_assigned_at", "lead_task_assignment", ["assigned_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_task_assignment_assigned_at", table_name="lead_task_assignment")
    op.drop_index("ix_lead_task_assignment_assigned_by", table_name="lead_task_assignment")
    op.drop_index("ix_lead_task_assignment_assigned_to", table_name="lead_task_assignment")
    op.drop_index("ix_lead_task_assignment_task_id", table_name="lead_task_assignment")
    op.drop_table("lead_task_assignment")
