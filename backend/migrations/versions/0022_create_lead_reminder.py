"""create lead reminder table

Revision ID: 0022_create_lead_reminder
Revises: 0021_create_lead_assignment_history
Create Date: 2026-05-08 19:10:30.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0022_create_lead_reminder"
down_revision: Union[str, None] = "0021_create_lead_assignment_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_reminder "
        "ON lead_reminder;"
    )
    op.drop_index("ix_lead_reminder_remind_at", table_name="lead_reminder")
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
    op.create_index(
        "ix_lead_reminder_lead_id",
        "lead_reminder",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_reminder_due_at",
        "lead_reminder",
        ["due_at"],
        unique=False,
    )
    op.create_index(
        "ix_lead_reminder_completed_at",
        "lead_reminder",
        ["completed_at"],
        unique=False,
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
    op.drop_index("ix_lead_reminder_completed_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_due_at", table_name="lead_reminder")
    op.drop_index("ix_lead_reminder_lead_id", table_name="lead_reminder")
    op.drop_table("lead_reminder")

    op.create_table(
        "lead_reminder",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("remind_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("reminder_message", sa.Text(), nullable=True),
        sa.Column(
            "is_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_reminder_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_reminder_lead_id",
        "lead_reminder",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_reminder_remind_at",
        "lead_reminder",
        ["remind_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_reminder "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_reminder "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
