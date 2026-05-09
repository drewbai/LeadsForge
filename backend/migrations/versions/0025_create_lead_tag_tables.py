"""create lead tag tables

Revision ID: 0025_create_lead_tag_tables
Revises: 0024_create_lead_email_log
Create Date: 2026-05-08 19:21:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0025_create_lead_tag_tables"
down_revision: Union[str, None] = "0024_create_lead_email_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_refresh_activity_lead_tag_link ON lead_tag_link;")
    op.drop_index("ix_lead_tag_link_tag_id", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_lead_id", table_name="lead_tag_link")
    op.drop_table("lead_tag_link")
    op.drop_table("leadtags")

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

    op.create_table(
        "lead_tag_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_tag_link_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["leadtag.id"],
            name="fk_lead_tag_link_tag_id_leadtag",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id", "tag_id", name="uq_lead_tag_link_lead_id_tag_id"),
    )
    op.create_index(
        "ix_lead_tag_link_lead_id",
        "lead_tag_link",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_tag_link_tag_id",
        "lead_tag_link",
        ["tag_id"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_tag_link "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_tag_link "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_refresh_activity_lead_tag_link ON lead_tag_link;")
    op.drop_index("ix_lead_tag_link_tag_id", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_lead_id", table_name="lead_tag_link")
    op.drop_table("lead_tag_link")
    op.drop_table("leadtag")

    op.create_table(
        "leadtags",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name", name="uq_leadtags_name"),
    )

    op.create_table(
        "lead_tag_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["lead_id"],
            ["leads.id"],
            name="fk_lead_tag_link_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["tag_id"],
            ["leadtags.id"],
            name="fk_lead_tag_link_tag_id_leadtags",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("lead_id", "tag_id", name="uq_lead_tag_link_lead_id_tag_id"),
    )
    op.create_index(
        "ix_lead_tag_link_lead_id",
        "lead_tag_link",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_tag_link_tag_id",
        "lead_tag_link",
        ["tag_id"],
        unique=False,
    )

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_tag_link "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_tag_link "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
