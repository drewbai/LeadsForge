"""add subscription table

Revision ID: 0061_add_subscription_table
Revises: 0056_add_lead_ranking_fields
Create Date: 2026-05-08 23:55:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0061_add_subscription_table"
down_revision: Union[str, None] = "0056_add_lead_ranking_fields"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "subscription",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type", sa.String(length=255), nullable=False),
        sa.Column("target_type", sa.String(length=32), nullable=False),
        sa.Column("target", sa.String(length=2048), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default=sa.text("true"),
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_subscription_event_type",
        "subscription",
        ["event_type"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_is_active",
        "subscription",
        ["is_active"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_event_type_is_active",
        "subscription",
        ["event_type", "is_active"],
        unique=False,
    )
    op.create_index(
        "ix_subscription_created_at",
        "subscription",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_subscription_created_at", table_name="subscription")
    op.drop_index("ix_subscription_event_type_is_active", table_name="subscription")
    op.drop_index("ix_subscription_is_active", table_name="subscription")
    op.drop_index("ix_subscription_event_type", table_name="subscription")
    op.drop_table("subscription")
