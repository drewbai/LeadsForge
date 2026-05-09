"""create lead sms log table

Revision ID: 0038_create_lead_sms_log
Revises: 0037_create_lead_call_log
Create Date: 2026-05-08 19:48:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0038_create_lead_sms_log"
down_revision: Union[str, None] = "0037_create_lead_call_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_sms_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("message_text", sa.Text(), nullable=False),
        sa.Column("provider_message_id", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("received_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_sms_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "direction IN ('inbound', 'outbound')",
            name="ck_lead_sms_log_direction",
        ),
        sa.CheckConstraint(
            "(direction = 'outbound' AND sent_at IS NOT NULL) "
            "OR (direction = 'inbound' AND received_at IS NOT NULL)",
            name="ck_lead_sms_log_direction_timestamp",
        ),
    )
    op.create_index("ix_lead_sms_log_lead_id", "lead_sms_log", ["lead_id"], unique=False)
    op.create_index("ix_lead_sms_log_direction", "lead_sms_log", ["direction"], unique=False)
    op.create_index("ix_lead_sms_log_provider_message_id", "lead_sms_log", ["provider_message_id"], unique=False)
    op.create_index("ix_lead_sms_log_sent_at", "lead_sms_log", ["sent_at"], unique=False)
    op.create_index("ix_lead_sms_log_received_at", "lead_sms_log", ["received_at"], unique=False)
    op.create_index("ix_lead_sms_log_created_at", "lead_sms_log", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_sms_log_created_at", table_name="lead_sms_log")
    op.drop_index("ix_lead_sms_log_received_at", table_name="lead_sms_log")
    op.drop_index("ix_lead_sms_log_sent_at", table_name="lead_sms_log")
    op.drop_index("ix_lead_sms_log_provider_message_id", table_name="lead_sms_log")
    op.drop_index("ix_lead_sms_log_direction", table_name="lead_sms_log")
    op.drop_index("ix_lead_sms_log_lead_id", table_name="lead_sms_log")
    op.drop_table("lead_sms_log")
