"""create lead tags and link tables

Revision ID: 0005_create_lead_tags_and_link
Revises: 0004_create_lead_assignment
Create Date: 2026-05-08 18:32:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0005_create_lead_tags_and_link"
down_revision: Union[str, None] = "0004_create_lead_assignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leadtags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadtags_name"),
    )

    op.create_table(
        "lead_tag_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_tag_link_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["leadtags.id"],
            name="fk_lead_tag_link_tag_id_leadtags",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id", "tag_id", name="uq_lead_tag_link_lead_id_tag_id"),
    )
    op.create_index(
        "ix_lead_tag_link_lead_id",
        "lead_tag_link",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_tag_link_tag_id",
        "lead_tag_link",
        ["tag_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_tag_link_tag_id", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_lead_id", table_name="lead_tag_link")
    op.drop_table("lead_tag_link")
    op.drop_table("leadtags")
