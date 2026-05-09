"""create lead reminder table

Revision ID: 0040_create_lead_reminder
Revises: 0039_create_lead_meeting_log
Create Date: 2026-05-08 19:51:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0040_create_lead_reminder"
down_revision: Union[str, None] = "0039_create_lead_meeting_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_reminder "
        "ON lead_reminder;"
    )
    op.execute(
        "ALTER TABLE lead_reminder_snooze "
        "DROP CONSTRAINT IF EXISTS fk_lead_reminder_snooze_reminder_id_lead_reminder;"
    )
    op.drop_index("ix_lead_reminder_completed_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_due_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_lead_id", table_name="lead_reminder")
    op.drop_table("lead_reminder")

    op.create_table(
        "lead_reminder",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
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
            name="fk_lead_reminder_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "(completed = false AND completed_at IS NULL) "
            "OR (completed = true AND completed_at IS NOT NULL)",
            name="ck_lead_reminder_completed_at_consistency",
        ),
    )
    op.create_index("ix_lead_reminder_lead_id", "lead_reminder", ["lead_id"], unique=False)
    op.create_index("ix_lead_reminder_due_at", "lead_reminder", ["due_at"], unique=False)
    op.create_index("ix_lead_reminder_completed", "lead_reminder", ["completed"], unique=False)
    op.create_index("ix_lead_reminder_completed_at", "lead_reminder", ["completed_at"], unique=False)
    op.create_index("ix_lead_reminder_created_by", "lead_reminder", ["created_by"], unique=False)
    op.create_index("ix_lead_reminder_created_at", "lead_reminder", ["created_at"], unique=False)

    op.create_foreign_key(
        "fk_lead_reminder_snooze_reminder_id_lead_reminder",
        "lead_reminder_snooze",
        "lead_reminder",
        ["reminder_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_reminder "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_reminder "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_reminder "
        "ON lead_reminder;"
    )
    op.execute(
        "ALTER TABLE lead_reminder_snooze "
        "DROP CONSTRAINT IF EXISTS fk_lead_reminder_snooze_reminder_id_lead_reminder;"
    )
    op.drop_index("ix_lead_reminder_created_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_created_by", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_completed_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_completed", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_due_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_lead_id", table_name="lead_reminder")
    op.drop_table("lead_reminder")

    op.create_table(
        "lead_reminder",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("reminder_text", sa.Text(), nullable=False),
        sa.Column("due_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_reminder_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_reminder_lead_id", "lead_reminder", ["lead_id"], unique=False)
    op.create_index("ix_lead_reminder_due_at", "lead_reminder", ["due_at"], unique=False)
    op.create_index("ix_lead_reminder_completed_at", "lead_reminder", ["completed_at"], unique=False)

    op.create_foreign_key(
        "fk_lead_reminder_snooze_reminder_id_lead_reminder",
        "lead_reminder_snooze",
        "lead_reminder",
        ["reminder_id"],
        ["id"],
        ondelete="CASCADE",
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_reminder "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_reminder "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
