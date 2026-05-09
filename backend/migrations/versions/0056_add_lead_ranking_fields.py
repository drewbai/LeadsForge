"""add lead ranking fields

Revision ID: 0056_add_lead_ranking_fields
Revises: 0055_create_lead_ai_embedding
Create Date: 2026-05-08 20:25:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0056_add_lead_ranking_fields"
down_revision: Union[str, None] = "0055_create_lead_ai_embedding"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("ranking_score", sa.Float(), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("ranking_explanation", sa.Text(), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("last_ranked_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_leads_ranking_score", "leads", ["ranking_score"], unique=False)
    op.create_index("ix_leads_last_ranked_at", "leads", ["last_ranked_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_last_ranked_at", table_name="leads")
    op.drop_index("ix_leads_ranking_score", table_name="leads")
    op.drop_column("leads", "last_ranked_at")
    op.drop_column("leads", "ranking_explanation")
    op.drop_column("leads", "ranking_score")
