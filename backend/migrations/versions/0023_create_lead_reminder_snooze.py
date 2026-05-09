"""create lead reminder snooze table

Revision ID: 0023_create_lead_reminder_snooze
Revises: 0022_create_lead_reminder
Create Date: 2026-05-08 19:16:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0023_create_lead_reminder_snooze"
down_revision: Union[str, None] = "0022_create_lead_reminder"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_reminder_snooze",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reminder_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("snoozed_until", sa.DateTime(timezone=True), nullable=False),
        sa.Column("snooze_reason", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["reminder_id"],
            ["lead_reminder.id"],
            name="fk_lead_reminder_snooze_reminder_id_lead_reminder",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_reminder_snooze_reminder_id",
        "lead_reminder_snooze",
        ["reminder_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_reminder_snooze_snoozed_until",
        "lead_reminder_snooze",
        ["snoozed_until"],
        unique=False,
    )
    op.create_index(
        "ix_lead_reminder_snooze_created_at",
        "lead_reminder_snooze",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_reminder_snooze_created_at",
        table_name="lead_reminder_snooze",
    )
    op.drop_index(
        "ix_lead_reminder_snooze_snoozed_until",
        table_name="lead_reminder_snooze",
    )
    op.drop_index(
        "ix_lead_reminder_snooze_reminder_id",
        table_name="lead_reminder_snooze",
    )
    op.drop_table("lead_reminder_snooze")
