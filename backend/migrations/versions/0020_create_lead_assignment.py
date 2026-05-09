"""create lead assignment table

Revision ID: 0020_create_lead_assignment
Revises: 0019_create_activity_timeline_triggers
Create Date: 2026-05-08 19:08:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0020_create_lead_assignment"
down_revision: Union[str, None] = "0019_create_activity_timeline_triggers"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_assignment "
        "ON lead_assignment;"
    )
    op.drop_index("ix_lead_assignment_assigned_to", table_name="lead_assignment")
    op.drop_index("ix_lead_assignment_lead_id", table_name="lead_assignment")
    op.drop_table("lead_assignment")

    op.create_table(
        "lead_assignment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", sa.Text(), nullable=False),
        sa.Column("assignment_reason", sa.Text(), nullable=True),
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
            name="fk_lead_assignment_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_assignment_lead_id",
        "lead_assignment",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_assignment_assigned_to",
        "lead_assignment",
        ["assigned_to"],
        unique=False,
    )
    op.create_index(
        "ix_lead_assignment_created_at",
        "lead_assignment",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_assignment "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_assignment "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_assignment "
        "ON lead_assignment;"
    )
    op.drop_index("ix_lead_assignment_created_at", table_name="lead_assignment")
    op.drop_index("ix_lead_assignment_assigned_to", table_name="lead_assignment")
    op.drop_index("ix_lead_assignment_lead_id", table_name="lead_assignment")
    op.drop_table("lead_assignment")

    op.create_table(
        "lead_assignment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("assigned_to", sa.Text(), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("assignment_notes", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_assignment_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_assignment_lead_id",
        "lead_assignment",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_assignment_assigned_to",
        "lead_assignment",
        ["assigned_to"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_assignment "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_assignment "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
