"""create lead webhook event table

Revision ID: 0026_create_lead_webhook_event
Revises: 0025_create_lead_tag_tables
Create Date: 2026-05-08 19:24:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0026_create_lead_webhook_event"
down_revision: Union[str, None] = "0025_create_lead_tag_tables"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_webhook_event "
        "ON lead_webhook_event;"
    )
    op.drop_index(
        "ix_lead_webhook_event_response_status",
        table_name="lead_webhook_event",
    )
    op.drop_index(
        "ix_lead_webhook_event_created_at",
        table_name="lead_webhook_event",
    )
    op.drop_index(
        "ix_lead_webhook_event_lead_id",
        table_name="lead_webhook_event",
    )
    op.drop_table("lead_webhook_event")

    op.create_table(
        "lead_webhook_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_source", sa.Text(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column(
            "received_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_webhook_event_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_webhook_event_lead_id",
        "lead_webhook_event",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_webhook_event_event_source",
        "lead_webhook_event",
        ["event_source"],
        unique=False,
    )
    op.create_index(
        "ix_lead_webhook_event_event_type",
        "lead_webhook_event",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        "ix_lead_webhook_event_received_at",
        "lead_webhook_event",
        ["received_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_webhook_event "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_webhook_event "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_webhook_event "
        "ON lead_webhook_event;"
    )
    op.drop_index(
        "ix_lead_webhook_event_received_at",
        table_name="lead_webhook_event",
    )
    op.drop_index(
        "ix_lead_webhook_event_event_type",
        table_name="lead_webhook_event",
    )
    op.drop_index(
        "ix_lead_webhook_event_event_source",
        table_name="lead_webhook_event",
    )
    op.drop_index(
        "ix_lead_webhook_event_lead_id",
        table_name="lead_webhook_event",
    )
    op.drop_table("lead_webhook_event")

    op.create_table(
        "lead_webhook_event",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_url", sa.Text(), nullable=False),
        sa.Column("payload_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("response_status", sa.Integer(), nullable=True),
        sa.Column("response_body", sa.Text(), nullable=True),
        sa.Column(
            "attempt_number",
            sa.Integer(),
            server_default=sa.text("1"),
            nullable=False,
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
            name="fk_lead_webhook_event_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_webhook_event_lead_id",
        "lead_webhook_event",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_webhook_event_created_at",
        "lead_webhook_event",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_lead_webhook_event_response_status",
        "lead_webhook_event",
        ["response_status"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_webhook_event "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_webhook_event "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
