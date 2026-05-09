"""add task table

Revision ID: 0059_add_task_table
Revises: 0057_add_lead_routing_fields
Create Date: 2026-05-08 23:36:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0059_add_task_table"
down_revision: Union[str, None] = "0057_add_lead_routing_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "task",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("task_type", sa.String(), nullable=False),
        sa.Column(
            "status",
            sa.String(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "payload",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "result",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'success', 'error')",
            name="ck_task_status",
        ),
    )
    op.create_index("ix_task_task_type", "task", ["task_type"], unique=False)
    op.create_index("ix_task_status", "task", ["status"], unique=False)
    op.create_index("ix_task_created_at", "task", ["created_at"], unique=False)
    op.create_index(
        "ix_task_status_created_at",
        "task",
        ["status", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_task_status_created_at", table_name="task")
    op.drop_index("ix_task_created_at", table_name="task")
    op.drop_index("ix_task_status", table_name="task")
    op.drop_index("ix_task_task_type", table_name="task")
    op.drop_table("task")
