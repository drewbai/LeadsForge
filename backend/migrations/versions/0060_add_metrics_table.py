"""add metrics table

Revision ID: 0060_add_metrics_table
Revises: 0061_add_subscription_table
Create Date: 2026-05-08 23:43:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0060_add_metrics_table"
down_revision: Union[str, None] = "0061_add_subscription_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "metric",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("metric_type", sa.String(), nullable=False),
        sa.Column(
            "value",
            sa.Float(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "labels",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_metric_metric_type", "metric", ["metric_type"], unique=False)
    op.create_index("ix_metric_created_at", "metric", ["created_at"], unique=False)
    op.create_index(
        "ix_metric_metric_type_created_at",
        "metric",
        ["metric_type", "created_at"],
        unique=False,
    )
    op.execute(
        "CREATE INDEX ix_metric_labels_gin ON metric USING gin (labels);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_metric_labels_gin;")
    op.drop_index("ix_metric_metric_type_created_at", table_name="metric")
    op.drop_index("ix_metric_created_at", table_name="metric")
    op.drop_index("ix_metric_metric_type", table_name="metric")
    op.drop_table("metric")
