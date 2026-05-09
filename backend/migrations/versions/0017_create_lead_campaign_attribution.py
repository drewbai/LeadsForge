"""create lead campaign attribution table

Revision ID: 0017_create_lead_campaign_attribution
Revises: 0016_create_lead_source
Create Date: 2026-05-08 18:56:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0017_create_lead_campaign_attribution"
down_revision: Union[str, None] = "0016_create_lead_source"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_campaign_attribution",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("campaign_name", sa.Text(), nullable=False),
        sa.Column("touchpoint_type", sa.Text(), nullable=False),
        sa.Column(
            "weight",
            sa.Numeric(),
            server_default=sa.text("1.0"),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "occurred_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_campaign_attribution_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "touchpoint_type IN ('first_touch', 'last_touch', 'assist')",
            name="ck_lead_campaign_attribution_touchpoint_type",
        ),
    )
    op.create_index(
        "ix_lead_campaign_attribution_lead_id",
        "lead_campaign_attribution",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_campaign_attribution_campaign_name",
        "lead_campaign_attribution",
        ["campaign_name"],
        unique=False,
    )
    op.create_index(
        "ix_lead_campaign_attribution_touchpoint_type",
        "lead_campaign_attribution",
        ["touchpoint_type"],
        unique=False,
    )
    op.create_index(
        "ix_lead_campaign_attribution_occurred_at",
        "lead_campaign_attribution",
        ["occurred_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_lead_campaign_attribution_occurred_at",
        table_name="lead_campaign_attribution",
    )
    op.drop_index(
        "ix_lead_campaign_attribution_touchpoint_type",
        table_name="lead_campaign_attribution",
    )
    op.drop_index(
        "ix_lead_campaign_attribution_campaign_name",
        table_name="lead_campaign_attribution",
    )
    op.drop_index(
        "ix_lead_campaign_attribution_lead_id",
        table_name="lead_campaign_attribution",
    )
    op.drop_table("lead_campaign_attribution")
