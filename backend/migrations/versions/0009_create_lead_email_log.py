"""create lead email log table

Revision ID: 0009_create_lead_email_log
Revises: 0008_create_lead_attachments
Create Date: 2026-05-08 18:42:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0009_create_lead_email_log"
down_revision: Union[str, None] = "0008_create_lead_attachments"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_email_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("direction", sa.Text(), nullable=False),
        sa.Column("subject", sa.Text(), nullable=True),
        sa.Column("body_preview", sa.Text(), nullable=True),
        sa.Column("message_id", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_email_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "direction IN ('outbound', 'inbound')",
            name="ck_lead_email_log_direction",
        ),
    )
    op.create_index(
        "ix_lead_email_log_lead_id",
        "lead_email_log",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_email_log_message_id",
        "lead_email_log",
        ["message_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_email_log_created_at",
        "lead_email_log",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_email_log_created_at", table_name="lead_email_log")
    op.drop_index("ix_lead_email_log_message_id", table_name="lead_email_log")
    op.drop_index("ix_lead_email_log_lead_id", table_name="lead_email_log")
    op.drop_table("lead_email_log")
