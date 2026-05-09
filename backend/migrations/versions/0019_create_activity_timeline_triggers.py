"""create activity timeline refresh triggers

Revision ID: 0019_create_activity_timeline_triggers
Revises: 0018_create_lead_activity_timeline
Create Date: 2026-05-08 19:02:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = "0019_create_activity_timeline_triggers"
down_revision: Union[str, None] = "0018_create_lead_activity_timeline"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


TRIGGER_TABLES = (
    "lead_note",
    "lead_email_log",
    "lead_reminder",
    "lead_assignment",
    "lead_audit_log",
    "lead_tag_link",
    "lead_score",
    "lead_score_history",
    "lead_webhook_event",
    "lead_merge_history",
)


CREATE_FUNCTION_SQL = """
CREATE OR REPLACE FUNCTION refresh_lead_activity_timeline()
RETURNS trigger
LANGUAGE plpgsql
AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY lead_activity_timeline;
    RETURN NULL;
END;
$$;
"""


DROP_FUNCTION_SQL = "DROP FUNCTION IF EXISTS refresh_lead_activity_timeline();"


def upgrade() -> None:
    op.execute(
        "CREATE UNIQUE INDEX IF NOT EXISTS uq_lead_activity_timeline_activity_id "
        "ON lead_activity_timeline (activity_type, id);"
    )

    op.execute(CREATE_FUNCTION_SQL)

    for table in TRIGGER_TABLES:
        trigger_name = f"trg_refresh_activity_{table}"
        op.execute(
            f"CREATE TRIGGER {trigger_name} "
            f"AFTER INSERT OR UPDATE OR DELETE ON {table} "
            f"FOR EACH STATEMENT "
            f"EXECUTE FUNCTION refresh_lead_activity_timeline();"
        )


def downgrade() -> None:
    for table in TRIGGER_TABLES:
        trigger_name = f"trg_refresh_activity_{table}"
        op.execute(f"DROP TRIGGER IF EXISTS {trigger_name} ON {table};")

    op.execute(DROP_FUNCTION_SQL)

    op.execute("DROP INDEX IF EXISTS uq_lead_activity_timeline_activity_id;")
