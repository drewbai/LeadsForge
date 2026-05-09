"""create lead task history table

Revision ID: 0042_create_lead_task_history
Revises: 0041_create_lead_task
Create Date: 2026-05-08 19:56:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0042_create_lead_task_history"
down_revision: Union[str, None] = "0041_create_lead_task"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_task_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("field_name", sa.Text(), nullable=True),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["task_id"],
            ["lead_task.id"],
            name="fk_lead_task_history_task_id_lead_task",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "action_type IN ('created', 'updated', 'status_change', "
            "'assigned', 'completed')",
            name="ck_lead_task_history_action_type",
        ),
    )
    op.create_index("ix_lead_task_history_task_id", "lead_task_history", ["task_id"], unique=False)
    op.create_index("ix_lead_task_history_action_type", "lead_task_history", ["action_type"], unique=False)
    op.create_index("ix_lead_task_history_field_name", "lead_task_history", ["field_name"], unique=False)
    op.create_index("ix_lead_task_history_changed_by", "lead_task_history", ["changed_by"], unique=False)
    op.create_index("ix_lead_task_history_changed_at", "lead_task_history", ["changed_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_task_history_changed_at", table_name="lead_task_history")
    op.drop_index("ix_lead_task_history_changed_by", table_name="lead_task_history")
    op.drop_index("ix_lead_task_history_field_name", table_name="lead_task_history")
    op.drop_index("ix_lead_task_history_action_type", table_name="lead_task_history")
    op.drop_index("ix_lead_task_history_task_id", table_name="lead_task_history")
    op.drop_table("lead_task_history")
