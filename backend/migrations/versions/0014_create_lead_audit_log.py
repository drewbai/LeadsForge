"""create lead audit log table

Revision ID: 0014_create_lead_audit_log
Revises: 0013_create_lead_notes
Create Date: 2026-05-08 18:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0014_create_lead_audit_log"
down_revision: Union[str, None] = "0013_create_lead_notes"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("field_changed", sa.Text(), nullable=True),
        sa.Column("old_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_audit_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_audit_log_lead_id",
        "lead_audit_log",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_audit_log_action_type",
        "lead_audit_log",
        ["action_type"],
        unique=False,
    )
    op.create_index(
        "ix_lead_audit_log_created_at",
        "lead_audit_log",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_audit_log_created_at", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_action_type", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_lead_id", table_name="lead_audit_log")
    op.drop_table("lead_audit_log")
