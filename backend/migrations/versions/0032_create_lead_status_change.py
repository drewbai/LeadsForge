"""create lead status change table

Revision ID: 0032_create_lead_status_change
Revises: 0031_create_lead_note
Create Date: 2026-05-08 19:37:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0032_create_lead_status_change"
down_revision: Union[str, None] = "0031_create_lead_note"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_status_change",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("previous_status", sa.Text(), nullable=True),
        sa.Column("new_status", sa.Text(), nullable=False),
        sa.Column("changed_by", sa.Text(), nullable=True),
        sa.Column("change_reason", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "changed_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_status_change_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_status_change_lead_id",
        "lead_status_change",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_status_change_new_status",
        "lead_status_change",
        ["new_status"],
        unique=False,
    )
    op.create_index(
        "ix_lead_status_change_previous_status",
        "lead_status_change",
        ["previous_status"],
        unique=False,
    )
    op.create_index(
        "ix_lead_status_change_changed_by",
        "lead_status_change",
        ["changed_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_status_change_changed_at",
        "lead_status_change",
        ["changed_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_status_change_changed_at", table_name="lead_status_change")
    op.drop_index("ix_lead_status_change_changed_by", table_name="lead_status_change")
    op.drop_index("ix_lead_status_change_previous_status", table_name="lead_status_change")
    op.drop_index("ix_lead_status_change_new_status", table_name="lead_status_change")
    op.drop_index("ix_lead_status_change_lead_id", table_name="lead_status_change")
    op.drop_table("lead_status_change")
