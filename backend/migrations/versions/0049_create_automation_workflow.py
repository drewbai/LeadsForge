"""create automation workflow table

Revision ID: 0049_create_automation_workflow
Revises: 0048_create_lead_segment_membership
Create Date: 2026-05-08 20:09:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0049_create_automation_workflow"
down_revision: Union[str, None] = "0048_create_lead_segment_membership"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "automation_workflow",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column("trigger_type", sa.Text(), nullable=False),
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
        sa.UniqueConstraint("name", name="uq_automation_workflow_name"),
        sa.CheckConstraint(
            "trigger_type IN ('lead_created', 'status_changed', "
            "'score_threshold', 'manual')",
            name="ck_automation_workflow_trigger_type",
        ),
    )
    op.create_index("ix_automation_workflow_is_active", "automation_workflow", ["is_active"], unique=False)
    op.create_index("ix_automation_workflow_trigger_type", "automation_workflow", ["trigger_type"], unique=False)
    op.create_index("ix_automation_workflow_created_by", "automation_workflow", ["created_by"], unique=False)
    op.create_index("ix_automation_workflow_created_at", "automation_workflow", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_automation_workflow_created_at", table_name="automation_workflow")
    op.drop_index("ix_automation_workflow_created_by", table_name="automation_workflow")
    op.drop_index("ix_automation_workflow_trigger_type", table_name="automation_workflow")
    op.drop_index("ix_automation_workflow_is_active", table_name="automation_workflow")
    op.drop_table("automation_workflow")
