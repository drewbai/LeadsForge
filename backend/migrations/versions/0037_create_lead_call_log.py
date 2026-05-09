"""create lead call log table

Revision ID: 0037_create_lead_call_log
Revises: 0036_create_lead_attachment_version
Create Date: 2026-05-08 19:46:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0037_create_lead_call_log"
down_revision: Union[str, None] = "0036_create_lead_attachment_version"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_call_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("call_duration_seconds", sa.Integer(), nullable=True),
        sa.Column("call_result", sa.Text(), nullable=True),
        sa.Column("transcript_preview", sa.Text(), nullable=True),
        sa.Column("provider_call_id", sa.Text(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_call_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name="ck_lead_call_log_direction",
        ),
        sa.CheckConstraint(
            "call_duration_seconds IS NULL OR call_duration_seconds >= 0",
            name="ck_lead_call_log_duration_non_negative",
        ),
    )
    op.create_index("ix_lead_call_log_lead_id", "lead_call_log", ["lead_id"], unique=False)
    op.create_index("ix_lead_call_log_direction", "lead_call_log", ["direction"], unique=False)
    op.create_index("ix_lead_call_log_call_result", "lead_call_log", ["call_result"], unique=False)
    op.create_index("ix_lead_call_log_provider_call_id", "lead_call_log", ["provider_call_id"], unique=False)
    op.create_index("ix_lead_call_log_started_at", "lead_call_log", ["started_at"], unique=False)
    op.create_index("ix_lead_call_log_created_at", "lead_call_log", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_call_log_created_at", table_name="lead_call_log")
    op.drop_index("ix_lead_call_log_started_at", table_name="lead_call_log")
    op.drop_index("ix_lead_call_log_provider_call_id", table_name="lead_call_log")
    op.drop_index("ix_lead_call_log_call_result", table_name="lead_call_log")
    op.drop_index("ix_lead_call_log_direction", table_name="lead_call_log")
    op.drop_index("ix_lead_call_log_lead_id", table_name="lead_call_log")
    op.drop_table("lead_call_log")
