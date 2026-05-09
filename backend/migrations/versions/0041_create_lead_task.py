"""create lead task table

Revision ID: 0041_create_lead_task
Revises: 0040_create_lead_reminder
Create Date: 2026-05-08 19:53:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0041_create_lead_task"
down_revision: Union[str, None] = "0040_create_lead_reminder"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_task",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "priority",
            sa.Text(),
            server_default=sa.text("'normal'"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Text(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column("assigned_to", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_task_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "priority IN ('low', 'normal', 'high', 'urgent')",
            name="ck_lead_task_priority",
        ),
        sa.CheckConstraint(
            "status IN ('pending', 'in_progress', 'completed', 'canceled')",
            name="ck_lead_task_status",
        ),
        sa.CheckConstraint(
            "(status = 'completed' AND completed_at IS NOT NULL) "
            "OR (status <> 'completed')",
            name="ck_lead_task_completed_at_consistency",
        ),
    )
    op.create_index("ix_lead_task_lead_id", "lead_task", ["lead_id"], unique=False)
    op.create_index("ix_lead_task_priority", "lead_task", ["priority"], unique=False)
    op.create_index("ix_lead_task_status", "lead_task", ["status"], unique=False)
    op.create_index("ix_lead_task_due_at", "lead_task", ["due_at"], unique=False)
    op.create_index("ix_lead_task_completed_at", "lead_task", ["completed_at"], unique=False)
    op.create_index("ix_lead_task_assigned_to", "lead_task", ["assigned_to"], unique=False)
    op.create_index("ix_lead_task_created_by", "lead_task", ["created_by"], unique=False)
    op.create_index("ix_lead_task_created_at", "lead_task", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_task_created_at", table_name="lead_task")
    op.drop_index("ix_lead_task_created_by", table_name="lead_task")
    op.drop_index("ix_lead_task_assigned_to", table_name="lead_task")
    op.drop_index("ix_lead_task_completed_at", table_name="lead_task")
    op.drop_index("ix_lead_task_due_at", table_name="lead_task")
    op.drop_index("ix_lead_task_status", table_name="lead_task")
    op.drop_index("ix_lead_task_priority", table_name="lead_task")
    op.drop_index("ix_lead_task_lead_id", table_name="lead_task")
    op.drop_table("lead_task")
