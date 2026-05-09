"""create lead segment rule table

Revision ID: 0047_create_lead_segment_rule
Revises: 0046_create_lead_segment
Create Date: 2026-05-08 20:07:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0047_create_lead_segment_rule"
down_revision: Union[str, None] = "0046_create_lead_segment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_segment_rule",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("segment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("field_name", sa.Text(), nullable=False),
        sa.Column("operator", sa.Text(), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "rule_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["segment_id"],
            ["lead_segment.id"],
            name="fk_lead_segment_rule_segment_id_lead_segment",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "operator IN ('=', '!=', '>', '<', '>=', '<=', 'contains', 'in')",
            name="ck_lead_segment_rule_operator",
        ),
    )
    op.create_index("ix_lead_segment_rule_segment_id", "lead_segment_rule", ["segment_id"], unique=False)
    op.create_index("ix_lead_segment_rule_field_name", "lead_segment_rule", ["field_name"], unique=False)
    op.create_index("ix_lead_segment_rule_rule_order", "lead_segment_rule", ["rule_order"], unique=False)
    op.create_index(
        "ix_lead_segment_rule_segment_id_rule_order",
        "lead_segment_rule",
        ["segment_id", "rule_order"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_segment_rule_segment_id_rule_order", table_name="lead_segment_rule")
    op.drop_index("ix_lead_segment_rule_rule_order", table_name="lead_segment_rule")
    op.drop_index("ix_lead_segment_rule_field_name", table_name="lead_segment_rule")
    op.drop_index("ix_lead_segment_rule_segment_id", table_name="lead_segment_rule")
    op.drop_table("lead_segment_rule")
