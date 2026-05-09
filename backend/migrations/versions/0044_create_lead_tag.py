"""create lead tag table

Revision ID: 0044_create_lead_tag
Revises: 0043_create_lead_task_assignment
Create Date: 2026-05-08 19:59:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0044_create_lead_tag"
down_revision: Union[str, None] = "0043_create_lead_task_assignment"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TABLE lead_tag_link "
        "DROP CONSTRAINT IF EXISTS fk_lead_tag_link_tag_id_leadtag;"
    )
    op.drop_table("leadtag")

    op.create_table(
        "leadtag",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.UniqueConstraint("name", name="uq_leadtag_name"),
    )
    op.create_index("ix_leadtag_created_at", "leadtag", ["created_at"], unique=False)

    op.create_foreign_key(
        "fk_lead_tag_link_tag_id_leadtag",
        "lead_tag_link",
        "leadtag",
        ["tag_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.execute(
        "ALTER TABLE lead_tag_link "
        "DROP CONSTRAINT IF EXISTS fk_lead_tag_link_tag_id_leadtag;"
    )
    op.drop_index("ix_leadtag_created_at", table_name="leadtag")
    op.drop_table("leadtag")

    op.create_table(
        "leadtag",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadtag_name"),
    )

    op.create_foreign_key(
        "fk_lead_tag_link_tag_id_leadtag",
        "lead_tag_link",
        "leadtag",
        ["tag_id"],
        ["id"],
        ondelete="CASCADE",
    )
