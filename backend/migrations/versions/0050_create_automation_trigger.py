"""create automation trigger table

Revision ID: 0050_create_automation_trigger
Revises: 0049_create_automation_workflow
Create Date: 2026-05-08 20:12:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0050_create_automation_trigger"
down_revision: Union[str, None] = "0049_create_automation_workflow"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "automation_trigger",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_type", sa.Text(), nullable=False),
        sa.Column("field_name", sa.Text(), nullable=True),
        sa.Column("operator", sa.Text(), nullable=True),
        sa.Column("value", sa.Text(), nullable=True),
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
            ["workflow_id"],
            ["automation_workflow.id"],
            name="fk_automation_trigger_workflow_id_automation_workflow",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "trigger_type IN ('lead_created', 'status_changed', 'score_threshold', 'manual')",
            name="ck_automation_trigger_trigger_type",
        ),
        sa.CheckConstraint(
            "operator IS NULL OR operator IN ('=', '!=', '>', '<', '>=', '<=')",
            name="ck_automation_trigger_operator",
        ),
    )
    op.create_index("ix_automation_trigger_workflow_id", "automation_trigger", ["workflow_id"], unique=False)
    op.create_index("ix_automation_trigger_trigger_type", "automation_trigger", ["trigger_type"], unique=False)
    op.create_index("ix_automation_trigger_field_name", "automation_trigger", ["field_name"], unique=False)
    op.create_index("ix_automation_trigger_created_at", "automation_trigger", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_automation_trigger_created_at", table_name="automation_trigger")
    op.drop_index("ix_automation_trigger_field_name", table_name="automation_trigger")
    op.drop_index("ix_automation_trigger_trigger_type", table_name="automation_trigger")
    op.drop_index("ix_automation_trigger_workflow_id", table_name="automation_trigger")
    op.drop_table("automation_trigger")
