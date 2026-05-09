"""create automation run log table

Revision ID: 0052_create_automation_run_log
Revises: 0051_create_automation_action
Create Date: 2026-05-08 20:14:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0052_create_automation_run_log"
down_revision: Union[str, None] = "0051_create_automation_action"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "automation_run_log",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("workflow_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("trigger_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "status",
            sa.Text(),
            server_default=sa.text("'pending'"),
            nullable=False,
        ),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("finished_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column(
            "action_results_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.ForeignKeyConstraint(
            ["workflow_id"],
            ["automation_workflow.id"],
            name="fk_automation_run_log_workflow_id_automation_workflow",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["trigger_id"],
            ["automation_trigger.id"],
            name="fk_automation_run_log_trigger_id_automation_trigger",
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_automation_run_log_lead_id_leads",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "status IN ('pending', 'running', 'success', 'failed', 'skipped')",
            name="ck_automation_run_log_status",
        ),
    )
    op.create_index("ix_automation_run_log_workflow_id", "automation_run_log", ["workflow_id"], unique=False)
    op.create_index("ix_automation_run_log_trigger_id", "automation_run_log", ["trigger_id"], unique=False)
    op.create_index("ix_automation_run_log_lead_id", "automation_run_log", ["lead_id"], unique=False)
    op.create_index("ix_automation_run_log_status", "automation_run_log", ["status"], unique=False)
    op.create_index("ix_automation_run_log_started_at", "automation_run_log", ["started_at"], unique=False)
    op.create_index("ix_automation_run_log_finished_at", "automation_run_log", ["finished_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_automation_run_log_finished_at", table_name="automation_run_log")
    op.drop_index("ix_automation_run_log_started_at", table_name="automation_run_log")
    op.drop_index("ix_automation_run_log_status", table_name="automation_run_log")
    op.drop_index("ix_automation_run_log_lead_id", table_name="automation_run_log")
    op.drop_index("ix_automation_run_log_trigger_id", table_name="automation_run_log")
    op.drop_index("ix_automation_run_log_workflow_id", table_name="automation_run_log")
    op.drop_table("automation_run_log")
