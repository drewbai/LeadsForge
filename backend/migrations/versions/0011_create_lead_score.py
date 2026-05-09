"""create lead score table

Revision ID: 0011_create_lead_score
Revises: 0010_create_lead_webhook_events
Create Date: 2026-05-08 18:45:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0011_create_lead_score"
down_revision: Union[str, None] = "0010_create_lead_webhook_events"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
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


def downgrade() -> None:
    op.drop_index("ix_lead_score_score_value", table_name="lead_score")
    op.drop_index("ix_lead_score_created_at", table_name="lead_score")
    op.drop_index("ix_lead_score_lead_id", table_name="lead_score")
    op.drop_table("lead_score")
