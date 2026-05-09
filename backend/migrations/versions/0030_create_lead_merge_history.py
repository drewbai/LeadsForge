"""create lead merge history table

Revision ID: 0030_create_lead_merge_history
Revises: 0029_create_lead_audit_log
Create Date: 2026-05-08 19:32:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0030_create_lead_merge_history"
down_revision: Union[str, None] = "0029_create_lead_audit_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_merge_history "
        "ON lead_merge_history;"
    )
    op.drop_index(
        "ix_lead_merge_history_created_at",
        table_name="lead_merge_history",
    )
    op.drop_index(
        "ix_lead_merge_history_target_lead_id",
        table_name="lead_merge_history",
    )
    op.drop_index(
        "ix_lead_merge_history_source_lead_id",
        table_name="lead_merge_history",
    )
    op.drop_table("lead_merge_history")

    op.create_table(
        "lead_merge_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merge_reason", sa.Text(), nullable=True),
        sa.Column("merged_by", sa.Text(), nullable=True),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
        sa.Column(
            "merged_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_lead_id"],
            ["leads.id"],
            name="fk_lead_merge_history_source_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_lead_id"],
            ["leads.id"],
            name="fk_lead_merge_history_target_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "source_lead_id <> target_lead_id",
            name="ck_lead_merge_history_source_target_distinct",
        ),
    )
    op.create_index(
        "ix_lead_merge_history_source_lead_id",
        "lead_merge_history",
        ["source_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_merge_history_target_lead_id",
        "lead_merge_history",
        ["target_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_merge_history_merged_by",
        "lead_merge_history",
        ["merged_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_merge_history_merged_at",
        "lead_merge_history",
        ["merged_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_merge_history "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_merge_history "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute(
        "DROP TRIGGER IF EXISTS trg_refresh_activity_lead_merge_history "
        "ON lead_merge_history;"
    )
    op.drop_index(
        "ix_lead_merge_history_merged_at",
        table_name="lead_merge_history",
    )
    op.drop_index(
        "ix_lead_merge_history_merged_by",
        table_name="lead_merge_history",
    )
    op.drop_index(
        "ix_lead_merge_history_target_lead_id",
        table_name="lead_merge_history",
    )
    op.drop_index(
        "ix_lead_merge_history_source_lead_id",
        table_name="lead_merge_history",
    )
    op.drop_table("lead_merge_history")

    op.create_table(
        "lead_merge_history",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("source_lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("target_lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("merge_reason", sa.Text(), nullable=True),
        sa.Column("performed_by", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["source_lead_id"],
            ["leads.id"],
            name="fk_lead_merge_history_source_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["target_lead_id"],
            ["leads.id"],
            name="fk_lead_merge_history_target_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.CheckConstraint(
            "source_lead_id <> target_lead_id",
            name="ck_lead_merge_history_source_target_distinct",
        ),
        sa.UniqueConstraint(
            "source_lead_id",
            "target_lead_id",
            name="uq_lead_merge_history_source_target",
        ),
    )
    op.create_index(
        "ix_lead_merge_history_source_lead_id",
        "lead_merge_history",
        ["source_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_merge_history_target_lead_id",
        "lead_merge_history",
        ["target_lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_merge_history_created_at",
        "lead_merge_history",
        ["created_at"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_merge_history "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_merge_history "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
