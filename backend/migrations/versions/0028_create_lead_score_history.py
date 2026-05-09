"""create lead score history table

Revision ID: 0028_create_lead_score_history
Revises: 0027_create_lead_score
Create Date: 2026-05-08 19:28:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0028_create_lead_score_history"
down_revision: Union[str, None] = "0027_create_lead_score"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_score_history "
        "ON lead_score_history;"
    )
    op.drop_index(
        "ix_lead_score_history_changed_at",
        table_name="lead_score_history",
    )
    op.drop_index(
        "ix_lead_score_history_lead_id",
        table_name="lead_score_history",
    )
    op.drop_table("lead_score_history")

    op.create_table(
        "lead_score_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_score", sa.Integer(), nullable=True),
        sa.Column("new_score", sa.Integer(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("changed_by", sa.Text(), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_score_history_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_score_history_lead_id",
        "lead_score_history",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_history_changed_by",
        "lead_score_history",
        ["changed_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_history_changed_at",
        "lead_score_history",
        ["changed_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_score_history "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_score_history "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_score_history "
        "ON lead_score_history;"
    )
    op.drop_index(
        "ix_lead_score_history_changed_at",
        table_name="lead_score_history",
    )
    op.drop_index(
        "ix_lead_score_history_changed_by",
        table_name="lead_score_history",
    )
    op.drop_index(
        "ix_lead_score_history_lead_id",
        table_name="lead_score_history",
    )
    op.drop_table("lead_score_history")

    op.create_table(
        "lead_score_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_score", sa.Integer(), nullable=True),
        sa.Column("new_score", sa.Integer(), nullable=False),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_score_history_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_score_history_lead_id",
        "lead_score_history",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_history_changed_at",
        "lead_score_history",
        ["changed_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_score_history "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_score_history "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
