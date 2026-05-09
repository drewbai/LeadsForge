"""create lead score table

Revision ID: 0027_create_lead_score
Revises: 0026_create_lead_webhook_event
Create Date: 2026-05-08 19:26:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0027_create_lead_score"
down_revision: Union[str, None] = "0026_create_lead_webhook_event"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_score "
        "ON lead_score;"
    )
    op.drop_index("ix_lead_score_score_value", table_name="lead_score")
    op.drop_index("ix_lead_score_created_at", table_name="lead_score")
    op.drop_index("ix_lead_score_lead_id", table_name="lead_score")
    op.drop_table("lead_score")

    op.create_table(
        "lead_score",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "score",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column("score_reason", sa.Text(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_score_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id", name="uq_lead_score_lead_id"),
    )
    op.create_index(
        "ix_lead_score_score",
        "lead_score",
        ["score"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_updated_at",
        "lead_score",
        ["updated_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_score "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_score "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_score "
        "ON lead_score;"
    )
    op.drop_index("ix_lead_score_updated_at", table_name="lead_score")
    op.drop_index("ix_lead_score_score", table_name="lead_score")
    op.drop_table("lead_score")

    op.create_table(
        "lead_score",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("score_value", sa.Integer(), nullable=False),
        sa.Column("score_reason", sa.Text(), nullable=True),
        sa.Column("model_version", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_score_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_score_lead_id",
        "lead_score",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_created_at",
        "lead_score",
        ["created_at"],
        unique=False,
    )
    op.create_index(
        "ix_lead_score_score_value",
        "lead_score",
        ["score_value"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_score "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_score "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
