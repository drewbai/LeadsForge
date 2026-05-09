"""create lead attachment version table

Revision ID: 0036_create_lead_attachment_version
Revises: 0035_create_lead_attachment
Create Date: 2026-05-08 19:44:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0036_create_lead_attachment_version"
down_revision: Union[str, None] = "0035_create_lead_attachment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "lead_attachment_version",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("attachment_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
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
            ["attachment_id"],
            ["lead_attachment.id"],
            name="fk_lead_attachment_version_attachment_id_lead_attachment",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "attachment_id",
            "version_number",
            name="uq_lead_attachment_version_attachment_id_version_number",
        ),
        sa.CheckConstraint(
            "version_number > 0",
            name="ck_lead_attachment_version_version_number_positive",
        ),
    )
    op.create_index(
        "ix_lead_attachment_version_attachment_id",
        "lead_attachment_version",
        ["attachment_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_attachment_version_uploaded_by",
        "lead_attachment_version",
        ["uploaded_by"],
        unique=False,
    )
    op.create_index(
        "ix_lead_attachment_version_uploaded_at",
        "lead_attachment_version",
        ["uploaded_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_lead_attachment_version_uploaded_at", table_name="lead_attachment_version")
    op.drop_index("ix_lead_attachment_version_uploaded_by", table_name="lead_attachment_version")
    op.drop_index("ix_lead_attachment_version_attachment_id", table_name="lead_attachment_version")
    op.drop_table("lead_attachment_version")
