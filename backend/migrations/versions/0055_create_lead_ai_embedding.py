"""create lead ai embedding table

Revision ID: 0055_create_lead_ai_embedding
Revises: 0054_create_lead_ai_insight
Create Date: 2026-05-08 20:20:00.000000

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

revision: str = "0055_create_lead_ai_embedding"
down_revision: Union[str, None] = "0054_create_lead_ai_insight"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


EMBEDDING_DIM = 1536


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS vector;")

    op.create_table(
        "lead_ai_embedding",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("lead_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("embedding_vector", Vector(EMBEDDING_DIM), nullable=False),
        sa.Column("model_name", sa.Text(), nullable=False),
        sa.Column(
            "generated_at",
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
            name="fk_lead_ai_embedding_lead_id_leads",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_lead_ai_embedding_lead_id",
        "lead_ai_embedding",
        ["lead_id"],
        unique=False,
    )
    op.create_index(
        "ix_lead_ai_embedding_model_name",
        "lead_ai_embedding",
        ["model_name"],
        unique=False,
    )
    op.create_index(
        "ix_lead_ai_embedding_generated_at",
        "lead_ai_embedding",
        ["generated_at"],
        unique=False,
    )

    op.execute(
        "CREATE INDEX ix_lead_ai_embedding_embedding_vector "
        "ON lead_ai_embedding USING ivfflat "
        "(embedding_vector vector_cosine_ops) WITH (lists = 100);"
    )


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_lead_ai_embedding_embedding_vector;")
    op.drop_index("ix_lead_ai_embedding_generated_at", table_name="lead_ai_embedding")
    op.drop_index("ix_lead_ai_embedding_model_name", table_name="lead_ai_embedding")
    op.drop_index("ix_lead_ai_embedding_lead_id", table_name="lead_ai_embedding")
    op.drop_table("lead_ai_embedding")
