"""add lead routing persistence columns

Revision ID: 0062_add_lead_routing_persistence
Revises: 0061_add_subscription_table
Create Date: 2026-05-10 00:00:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0062_add_lead_routing_persistence"
down_revision: Union[str, None] = "0061_add_subscription_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("leads", sa.Column("assigned_to", sa.String(length=128), nullable=True))
    op.add_column("leads", sa.Column("routing_reason", sa.String(length=256), nullable=True))
    op.add_column(
        "leads",
        sa.Column("last_routed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(op.f("ix_leads_assigned_to"), "leads", ["assigned_to"], unique=False)
    op.create_index(op.f("ix_leads_last_routed_at"), "leads", ["last_routed_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_leads_last_routed_at"), table_name="leads")
    op.drop_index(op.f("ix_leads_assigned_to"), table_name="leads")
    op.drop_column("leads", "last_routed_at")
    op.drop_column("leads", "routing_reason")
    op.drop_column("leads", "assigned_to")
