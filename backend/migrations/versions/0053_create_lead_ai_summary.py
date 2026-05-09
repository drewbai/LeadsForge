"""create lead ai summary table

Revision ID: 0053_create_lead_ai_summary
Revises: 0052_create_automation_run_log
Create Date: 2026-05-08 20:18:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0053_create_lead_ai_summary"
down_revision: Union[str, None] = "0052_create_automation_run_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_ai_summary",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("summary_text", sa.Text(), nullable=False),
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
            name="fk_lead_ai_summary_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_ai_summary_lead_id", "lead_ai_summary", ["lead_id"], unique=False)
    op.create_index("ix_lead_ai_summary_model_name", "lead_ai_summary", ["model_name"], unique=False)
    op.create_index("ix_lead_ai_summary_generated_at", "lead_ai_summary", ["generated_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_ai_summary_generated_at", table_name="lead_ai_summary")
    op.drop_index("ix_lead_ai_summary_model_name", table_name="lead_ai_summary")
    op.drop_index("ix_lead_ai_summary_lead_id", table_name="lead_ai_summary")
    op.drop_table("lead_ai_summary")
