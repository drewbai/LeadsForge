"""add lead status enum

Revision ID: 0003_add_lead_status_enum
Revises: 0002_create_lead_activity_log
Create Date: 2026-05-08 18:28:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0003_add_lead_status_enum"
down_revision: Union[str, None] = "0002_create_lead_activity_log"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


LEAD_STATUS_VALUES = (
    "new",
    "contacted",
    "in_progress",
    "qualified",
    "unqualified",
    "converted",
    "archived",
)

lead_status_enum = postgresql.ENUM(
    *LEAD_STATUS_VALUES,
    name="leadstatus",
    create_type=False,
)


def upgrade() -> None:
    bind = op.get_bind()
    lead_status_enum.create(bind, checkfirst=True)

    op.alter_column(
        "leads",
        "status",
        existing_type=sa.Text(),
        type_=lead_status_enum,
        existing_nullable=False,
        nullable=False,
        existing_server_default=sa.text("'new'"),
        server_default=sa.text("'new'::leadstatus"),
        postgresql_using="status::text::leadstatus",
    )


def downgrade() -> None:
    op.alter_column(
        "leads",
        "status",
        existing_type=lead_status_enum,
        type_=sa.Text(),
        existing_nullable=False,
        nullable=False,
        existing_server_default=sa.text("'new'::leadstatus"),
        server_default=sa.text("'new'"),
        postgresql_using="status::text",
    )

    bind = op.get_bind()
    lead_status_enum.drop(bind, checkfirst=True)
