"""create lead pipeline stages table

Revision ID: 0006_create_lead_pipeline_stages
Revises: 0005_create_lead_tags_and_link
Create Date: 2026-05-08 18:37:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006_create_lead_pipeline_stages"
down_revision: Union[str, None] = "0005_create_lead_tags_and_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leadpipelinestage",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadpipelinestage_name"),
    )

    op.add_column(
        "leads",
        sa.Column("pipeline_stage_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        "leadpipelinestage",
        ["pipeline_stage_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_leads_pipeline_stage_id",
        "leads",
        ["pipeline_stage_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_leads_pipeline_stage_id", table_name="leads")
    op.drop_constraint(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        type_="foreignkey",
    )
    op.drop_column("leads", "pipeline_stage_id")
    op.drop_table("leadpipelinestage")
