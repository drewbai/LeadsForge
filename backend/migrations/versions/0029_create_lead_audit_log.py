"""create lead audit log table

Revision ID: 0029_create_lead_audit_log
Revises: 0028_create_lead_score_history
Create Date: 2026-05-08 19:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0029_create_lead_audit_log"
down_revision: Union[str, None] = "0028_create_lead_score_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_audit_log "
        "ON lead_audit_log;"
    )
    op.drop_index("ix_lead_audit_log_created_at", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_action_type", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_lead_id", table_name="lead_audit_log")
    op.drop_table("lead_audit_log")

    op.create_table(
        "lead_audit_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column("field_name", sa.Text(), nullable=True),
        sa.Column("previous_value", sa.Text(), nullable=True),
        sa.Column("new_value", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
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
        "ix_lead_audit_log_field_name",
        "lead_audit_log",
        ["field_name"],
        unique=False,
    )
    op.create_index(
        "ix_lead_audit_log_changed_by",
        "lead_audit_log",
        ["changed_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_audit_log_created_at",
        "lead_audit_log",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_audit_log "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_audit_log "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_audit_log "
        "ON lead_audit_log;"
    )
    op.drop_index("ix_lead_audit_log_created_at", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_changed_by", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_field_name", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_action_type", table_name="lead_audit_log")
    op.drop_index("ix_lead_audit_log_lead_id", table_name="lead_audit_log")
    op.drop_table("lead_audit_log")

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

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_audit_log "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_audit_log "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
