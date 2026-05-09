"""create lead ai insight table

Revision ID: 0054_create_lead_ai_insight
Revises: 0053_create_lead_ai_summary
Create Date: 2026-05-08 20:19:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0054_create_lead_ai_insight"
down_revision: Union[str, None] = "0053_create_lead_ai_summary"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_ai_insight",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("insight_type", sa.Text(), nullable=False),
        sa.Column("insight_text", sa.Text(), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
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
            name="fk_lead_ai_insight_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "insight_type IN ('next_best_action', 'risk', 'opportunity', 'persona', 'sentiment')",
            name="ck_lead_ai_insight_insight_type",
        ),
    )
    op.create_index("ix_lead_ai_insight_lead_id", "lead_ai_insight", ["lead_id"], unique=False)
    op.create_index("ix_lead_ai_insight_insight_type", "lead_ai_insight", ["insight_type"], unique=False)
    op.create_index("ix_lead_ai_insight_model_name", "lead_ai_insight", ["model_name"], unique=False)
    op.create_index("ix_lead_ai_insight_generated_at", "lead_ai_insight", ["generated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_ai_insight_generated_at", table_name="lead_ai_insight")
    op.drop_index("ix_lead_ai_insight_model_name", table_name="lead_ai_insight")
    op.drop_index("ix_lead_ai_insight_insight_type", table_name="lead_ai_insight")
    op.drop_index("ix_lead_ai_insight_lead_id", table_name="lead_ai_insight")
    op.drop_table("lead_ai_insight")
