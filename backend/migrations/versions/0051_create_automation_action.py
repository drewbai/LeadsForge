"""create automation action table

Revision ID: 0051_create_automation_action
Revises: 0050_create_automation_trigger
Create Date: 2026-05-08 20:13:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0051_create_automation_action"
down_revision: Union[str, None] = "0050_create_automation_trigger"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "automation_action",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action_type", sa.Text(), nullable=False),
        sa.Column(
            "action_order",
            sa.Integer(),
            server_default=sa.text("0"),
            nullable=False,
        ),
        sa.Column(
            "config_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["automation_workflow.id"],
            name="fk_automation_action_workflow_id_automation_workflow",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "action_type IN ('send_email', 'send_sms', 'create_task', 'update_status', 'add_tag', 'webhook')",
            name="ck_automation_action_action_type",
        ),
    )
    op.create_index("ix_automation_action_workflow_id", "automation_action", ["workflow_id"], unique=False)
    op.create_index("ix_automation_action_action_type", "automation_action", ["action_type"], unique=False)
    op.create_index("ix_automation_action_action_order", "automation_action", ["action_order"], unique=False)
    op.create_index(
        "ix_automation_action_workflow_id_action_order",
        "automation_action",
        ["workflow_id", "action_order"],
        unique=False,
    )
    op.create_index("ix_automation_action_created_at", "automation_action", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_automation_action_created_at", table_name="automation_action")
    op.drop_index("ix_automation_action_workflow_id_action_order", table_name="automation_action")
    op.drop_index("ix_automation_action_action_order", table_name="automation_action")
    op.drop_index("ix_automation_action_action_type", table_name="automation_action")
    op.drop_index("ix_automation_action_workflow_id", table_name="automation_action")
    op.drop_table("automation_action")
