"""create lead note table

Revision ID: 0031_create_lead_note
Revises: 0030_create_lead_merge_history
Create Date: 2026-05-08 19:34:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0031_create_lead_note"
down_revision: Union[str, None] = "0030_create_lead_merge_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_note "
        "ON lead_note;"
    )
    op.drop_index("ix_lead_note_created_at", table_name="lead_note")
    op.drop_index("ix_lead_note_lead_id", table_name="lead_note")
    op.drop_table("lead_note")

    op.create_table(
        "lead_note",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author", sa.Text(), nullable=True),
        sa.Column("note_text", sa.Text(), nullable=False),
        sa.Column(
            "pinned",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
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
            name="fk_lead_note_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_note_lead_id",
        "lead_note",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_note_author",
        "lead_note",
        ["author"],
        unique=False,
    )
    op.create_index(
        "ix_lead_note_pinned",
        "lead_note",
        ["pinned"],
        unique=False,
    )
    op.create_index(
        "ix_lead_note_created_at",
        "lead_note",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_note "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_note "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_note "
        "ON lead_note;"
    )
    op.drop_index("ix_lead_note_created_at", table_name="lead_note")
    op.drop_index("ix_lead_note_pinned", table_name="lead_note")
    op.drop_index("ix_lead_note_author", table_name="lead_note")
    op.drop_index("ix_lead_note_lead_id", table_name="lead_note")
    op.drop_table("lead_note")

    op.create_table(
        "lead_note",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("author", sa.Text(), nullable=False),
        sa.Column("note_body", sa.Text(), nullable=False),
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
            name="fk_lead_note_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_note_lead_id",
        "lead_note",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_note_created_at",
        "lead_note",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_note "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_note "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
