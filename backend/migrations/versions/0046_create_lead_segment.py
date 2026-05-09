"""create lead segment table

Revision ID: 0046_create_lead_segment
Revises: 0045_create_lead_tag_link
Create Date: 2026-05-08 20:06:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0046_create_lead_segment"
down_revision: Union[str, None] = "0045_create_lead_tag_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_segment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "segment_type",
            sa.Text(),
            server_default=sa.text("'dynamic'"),
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column("created_by", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_lead_segment_name"),
        sa.CheckConstraint(
            "segment_type IN ('dynamic', 'static')",
            name="ck_lead_segment_segment_type",
        ),
    )
    op.create_index("ix_lead_segment_segment_type", "lead_segment", ["segment_type"], unique=False)
    op.create_index("ix_lead_segment_is_active", "lead_segment", ["is_active"], unique=False)
    op.create_index("ix_lead_segment_created_by", "lead_segment", ["created_by"], unique=False)
    op.create_index("ix_lead_segment_created_at", "lead_segment", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_segment_created_at", table_name="lead_segment")
    op.drop_index("ix_lead_segment_created_by", table_name="lead_segment")
    op.drop_index("ix_lead_segment_is_active", table_name="lead_segment")
    op.drop_index("ix_lead_segment_segment_type", table_name="lead_segment")
    op.drop_table("lead_segment")
