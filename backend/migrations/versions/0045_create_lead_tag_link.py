"""create lead tag link table

Revision ID: 0045_create_lead_tag_link
Revises: 0044_create_lead_tag
Create Date: 2026-05-08 20:01:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0045_create_lead_tag_link"
down_revision: Union[str, None] = "0044_create_lead_tag"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_refresh_activity_lead_tag_link ON lead_tag_link;")
    op.drop_index("ix_lead_tag_link_tag_id", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_lead_id", table_name="lead_tag_link")
    op.drop_table("lead_tag_link")

    op.create_table(
        "lead_tag_link",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tag_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("applied_by", sa.Text(), nullable=True),
        sa.Column(
            "applied_at",
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
    op.create_index("ix_lead_tag_link_lead_id", "lead_tag_link", ["lead_id"], unique=False)
    op.create_index("ix_lead_tag_link_tag_id", "lead_tag_link", ["tag_id"], unique=False)
    op.create_index("ix_lead_tag_link_applied_by", "lead_tag_link", ["applied_by"], unique=False)
    op.create_index("ix_lead_tag_link_applied_at", "lead_tag_link", ["applied_at"], unique=False)

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_tag_link "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_tag_link "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_refresh_activity_lead_tag_link ON lead_tag_link;")
    op.drop_index("ix_lead_tag_link_applied_at", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_applied_by", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_tag_id", table_name="lead_tag_link")
    op.drop_index("ix_lead_tag_link_lead_id", table_name="lead_tag_link")
    op.drop_table("lead_tag_link")

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
    op.create_index("ix_lead_tag_link_lead_id", "lead_tag_link", ["lead_id"], unique=False)
    op.create_index("ix_lead_tag_link_tag_id", "lead_tag_link", ["tag_id"], unique=False)

    op.execute(
        "CREATE TRIGGER trg_refresh_activity_lead_tag_link "
        "AFTER INSERT OR UPDATE OR DELETE ON lead_tag_link "
        "FOR EACH STATEMENT "
        "EXECUTE FUNCTION refresh_lead_activity_timeline();"
    )
