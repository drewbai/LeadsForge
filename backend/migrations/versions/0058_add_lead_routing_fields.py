"""add lead routing fields

Revision ID: 0058_add_lead_routing_fields
Revises: 0057_add_task_table
Create Date: 2026-05-08 22:50:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0058_add_lead_routing_fields"
down_revision: Union[str, None] = "0057_add_task_table"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "leads",
        sa.Column("assigned_to", sa.String(), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("routing_reason", sa.Text(), nullable=True),
    )
    op.add_column(
        "leads",
        sa.Column("last_routed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_leads_assigned_to", "leads", ["assigned_to"], unique=False)
    op.create_index("ix_leads_last_routed_at", "leads", ["last_routed_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_leads_last_routed_at", table_name="leads")
    op.drop_index("ix_leads_assigned_to", table_name="leads")
    op.drop_column("leads", "last_routed_at")
    op.drop_column("leads", "routing_reason")
    op.drop_column("leads", "assigned_to")
