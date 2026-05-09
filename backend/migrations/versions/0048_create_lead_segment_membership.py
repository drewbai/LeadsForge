"""create lead segment membership table

Revision ID: 0048_create_lead_segment_membership
Revises: 0047_create_lead_segment_rule
Create Date: 2026-05-08 20:08:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0048_create_lead_segment_membership"
down_revision: Union[str, None] = "0047_create_lead_segment_rule"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_segment_membership",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("segment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "membership_source",
            sa.Text(),
            server_default=sa.text("'dynamic'"),
            nullable=False,
        ),
        sa.Column("added_by", sa.Text(), nullable=True),
        sa.Column(
            "added_at",
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
            ["segment_id"],
            ["lead_segment.id"],
            name="fk_lead_segment_membership_segment_id_lead_segment",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_segment_membership_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "segment_id",
            "lead_id",
            name="uq_lead_segment_membership_segment_id_lead_id",
        ),
        sa.CheckConstraint(
            "membership_source IN ('dynamic', 'static')",
            name="ck_lead_segment_membership_membership_source",
        ),
    )
    op.create_index("ix_lead_segment_membership_segment_id", "lead_segment_membership", ["segment_id"], unique=False)
    op.create_index("ix_lead_segment_membership_lead_id", "lead_segment_membership", ["lead_id"], unique=False)
    op.create_index(
        "ix_lead_segment_membership_membership_source",
        "lead_segment_membership",
        ["membership_source"],
        unique=False,
    )
    op.create_index("ix_lead_segment_membership_added_by", "lead_segment_membership", ["added_by"], unique=False)
    op.create_index("ix_lead_segment_membership_added_at", "lead_segment_membership", ["added_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_segment_membership_added_at", table_name="lead_segment_membership")
    op.drop_index("ix_lead_segment_membership_added_by", table_name="lead_segment_membership")
    op.drop_index("ix_lead_segment_membership_membership_source", table_name="lead_segment_membership")
    op.drop_index("ix_lead_segment_membership_lead_id", table_name="lead_segment_membership")
    op.drop_index("ix_lead_segment_membership_segment_id", table_name="lead_segment_membership")
    op.drop_table("lead_segment_membership")
