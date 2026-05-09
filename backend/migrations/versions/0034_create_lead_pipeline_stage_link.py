"""create lead pipeline stage link table

Revision ID: 0034_create_lead_pipeline_stage_link
Revises: 0033_create_lead_pipeline_stage
Create Date: 2026-05-08 19:40:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0034_create_lead_pipeline_stage_link"
down_revision: Union[str, None] = "0033_create_lead_pipeline_stage"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_pipeline_stage_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("stage_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("assigned_by", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_pipeline_stage_link_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["stage_id"],
            ["leadpipelinestage.id"],
            name="fk_lead_pipeline_stage_link_stage_id_leadpipelinestage",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id", name="uq_lead_pipeline_stage_link_lead_id"),
    )
    op.create_index(
        "ix_lead_pipeline_stage_link_stage_id",
        "lead_pipeline_stage_link",
        ["stage_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_pipeline_stage_link_assigned_at",
        "lead_pipeline_stage_link",
        ["assigned_at"],
        unique=False,
    )
    op.create_index(
        "ix_lead_pipeline_stage_link_assigned_by",
        "lead_pipeline_stage_link",
        ["assigned_by"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_pipeline_stage_link_assigned_by", table_name="lead_pipeline_stage_link")
    op.drop_index("ix_lead_pipeline_stage_link_assigned_at", table_name="lead_pipeline_stage_link")
    op.drop_index("ix_lead_pipeline_stage_link_stage_id", table_name="lead_pipeline_stage_link")
    op.drop_table("lead_pipeline_stage_link")
