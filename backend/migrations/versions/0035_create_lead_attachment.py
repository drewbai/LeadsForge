"""create lead attachment table

Revision ID: 0035_create_lead_attachment
Revises: 0034_create_lead_pipeline_stage_link
Create Date: 2026-05-08 19:40:30.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0035_create_lead_attachment"
down_revision: Union[str, None] = "0034_create_lead_pipeline_stage_link"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_index("ix_lead_attachment_lead_id", table_name="lead_attachment")
    op.drop_table("lead_attachment")

    op.create_table(
        "lead_attachment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("file_type", sa.Text(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("uploaded_by", sa.Text(), nullable=True),
        sa.Column(
            "uploaded_at",
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
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_attachment_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_attachment_lead_id", "lead_attachment", ["lead_id"], unique=False)
    op.create_index("ix_lead_attachment_uploaded_by", "lead_attachment", ["uploaded_by"], unique=False)
    op.create_index("ix_lead_attachment_uploaded_at", "lead_attachment", ["uploaded_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_lead_attachment_uploaded_at", table_name="lead_attachment")
    op.drop_index("ix_lead_attachment_uploaded_by", table_name="lead_attachment")
    op.drop_index("ix_lead_attachment_lead_id", table_name="lead_attachment")
    op.drop_table("lead_attachment")

    op.create_table(
        "lead_attachment",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("file_name", sa.Text(), nullable=False),
        sa.Column("file_type", sa.Text(), nullable=True),
        sa.Column("file_size", sa.Integer(), nullable=True),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_attachment_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_lead_attachment_lead_id", "lead_attachment", ["lead_id"], unique=False)
