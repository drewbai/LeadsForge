"""create lead source table

Revision ID: 0016_create_lead_source
Revises: 0015_create_lead_merge_history
Create Date: 2026-05-08 18:55:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016_create_lead_source"
down_revision: Union[str, None] = "0015_create_lead_merge_history"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "leadsource",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadsource_name"),
    )

    op.add_column(
        "leads",
        sa.Column("source_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_leads_source_id_leadsource",
        "leads",
        "leadsource",
        ["source_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_index(
        "ix_leads_source_id",
        "leads",
        ["source_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_leads_source_id", table_name="leads")
    op.drop_constraint(
        "fk_leads_source_id_leadsource",
        "leads",
        type_="foreignkey",
    )
    op.drop_column("leads", "source_id")
    op.drop_table("leadsource")
