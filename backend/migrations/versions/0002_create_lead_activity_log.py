"""create lead activity log table

Revision ID: 0002_create_lead_activity_log
Revises: 0001_create_leads_table
Create Date: 2026-05-08 18:23:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0002_create_lead_activity_log"
down_revision: Union[str, None] = "0001_create_leads_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_activity_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("activity_type", sa.Text(), nullable=False),
        sa.Column("activity_details", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_activity_log_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_activity_log_lead_id",
        "lead_activity_log",
        ["lead_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_activity_log_lead_id", table_name="lead_activity_log")
    op.drop_table("lead_activity_log")
