"""create lead pipeline stage table

Revision ID: 0033_create_lead_pipeline_stage
Revises: 0032_create_lead_status_change
Create Date: 2026-05-08 19:37:30.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0033_create_lead_pipeline_stage"
down_revision: Union[str, None] = "0032_create_lead_status_change"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_leads_pipeline_stage_id", table_name="leads")
    op.drop_constraint(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        type_="foreignkey",
    )
    op.drop_table("leadpipelinestage")

    op.create_table(
        "leadpipelinestage",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.Column(
            "is_default",
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadpipelinestage_name"),
    )
    op.create_index("ix_leadpipelinestage_position", "leadpipelinestage", ["position"], unique=False)
    op.create_index("ix_leadpipelinestage_is_default", "leadpipelinestage", ["is_default"], unique=False)

    op.create_foreign_key(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        "leadpipelinestage",
        ["pipeline_stage_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_leads_pipeline_stage_id", "leads", ["pipeline_stage_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_pipeline_stage_id", table_name="leads")
    op.drop_constraint(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        type_="foreignkey",
    )
    op.drop_index("ix_leadpipelinestage_is_default", table_name="leadpipelinestage")
    op.drop_index("ix_leadpipelinestage_position", table_name="leadpipelinestage")
    op.drop_table("leadpipelinestage")

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

    op.create_foreign_key(
        "fk_leads_pipeline_stage_id_leadpipelinestage",
        "leads",
        "leadpipelinestage",
        ["pipeline_stage_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index("ix_leads_pipeline_stage_id", "leads", ["pipeline_stage_id"], unique=False)
