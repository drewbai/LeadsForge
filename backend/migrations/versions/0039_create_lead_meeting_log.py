"""create lead meeting log table

Revision ID: 0039_create_lead_meeting_log
Revises: 0038_create_lead_sms_log
Create Date: 2026-05-08 19:49:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0039_create_lead_meeting_log"
down_revision: Union[str, None] = "0038_create_lead_sms_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_meeting_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("meeting_type", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("scheduled_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("scheduled_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_start", sa.DateTime(timezone=True), nullable=True),
        sa.Column("actual_end", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_meeting_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "scheduled_end IS NULL OR scheduled_start IS NULL "
            "OR scheduled_end >= scheduled_start",
            name="ck_lead_meeting_log_scheduled_range",
        ),
        sa.CheckConstraint(
            "actual_end IS NULL OR actual_start IS NULL "
            "OR actual_end >= actual_start",
            name="ck_lead_meeting_log_actual_range",
        ),
    )
    op.create_index("ix_lead_meeting_log_lead_id", "lead_meeting_log", ["lead_id"], unique=False)
    op.create_index("ix_lead_meeting_log_meeting_type", "lead_meeting_log", ["meeting_type"], unique=False)
    op.create_index("ix_lead_meeting_log_scheduled_start", "lead_meeting_log", ["scheduled_start"], unique=False)
    op.create_index("ix_lead_meeting_log_actual_start", "lead_meeting_log", ["actual_start"], unique=False)
    op.create_index("ix_lead_meeting_log_created_by", "lead_meeting_log", ["created_by"], unique=False)
    op.create_index("ix_lead_meeting_log_created_at", "lead_meeting_log", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_meeting_log_created_at", table_name="lead_meeting_log")
    op.drop_index("ix_lead_meeting_log_created_by", table_name="lead_meeting_log")
    op.drop_index("ix_lead_meeting_log_actual_start", table_name="lead_meeting_log")
    op.drop_index("ix_lead_meeting_log_scheduled_start", table_name="lead_meeting_log")
    op.drop_index("ix_lead_meeting_log_meeting_type", table_name="lead_meeting_log")
    op.drop_index("ix_lead_meeting_log_lead_id", table_name="lead_meeting_log")
    op.drop_table("lead_meeting_log")
