"""create lead activity timeline materialized view

Revision ID: 0018_create_lead_activity_timeline
Revises: 0017_create_lead_campaign_attribution
Create Date: 2026-05-08 19:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

revision: str = "0018_create_lead_activity_timeline"
down_revision: Union[str, None] = "0017_create_lead_campaign_attribution"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


CREATE_VIEW_SQL = """
CREATE MATERIALIZED VIEW lead_activity_timeline AS
SELECT
    id,
    lead_id,
    'note'::text AS activity_type,
    created_at AS activity_timestamp,
    'Note by ' || author || ': ' || left(note_body, 200) AS summary,
    jsonb_build_object(
        'author', author,
        'note_body', note_body,
        'updated_at', updated_at
    ) AS metadata_json
FROM lead_note

UNION ALL

SELECT
    id,
    lead_id,
    'email'::text AS activity_type,
    created_at AS activity_timestamp,
    direction || ' email: ' || coalesce(subject, '(no subject)') AS summary,
    jsonb_build_object(
        'direction', direction,
        'subject', subject,
        'body_preview', body_preview,
        'message_id', message_id
    ) AS metadata_json
FROM lead_email_log

UNION ALL

SELECT
    id,
    lead_id,
    'reminder'::text AS activity_type,
    created_at AS activity_timestamp,
    'Reminder for ' || remind_at::text || ': ' ||
        coalesce(reminder_message, '') AS summary,
    jsonb_build_object(
        'remind_at', remind_at,
        'reminder_message', reminder_message,
        'is_completed', is_completed
    ) AS metadata_json
FROM lead_reminder

UNION ALL

SELECT
    id,
    lead_id,
    'assignment'::text AS activity_type,
    assigned_at AS activity_timestamp,
    'Assigned to ' || assigned_to AS summary,
    jsonb_build_object(
        'assigned_to', assigned_to,
        'assignment_notes', assignment_notes
    ) AS metadata_json
FROM lead_assignment

UNION ALL

SELECT
    id,
    lead_id,
    'audit'::text AS activity_type,
    created_at AS activity_timestamp,
    action_type || coalesce(' ' || field_changed, '') ||
        coalesce(': ' || old_value || ' -> ' || new_value, '') AS summary,
    jsonb_build_object(
        'action_type', action_type,
        'field_changed', field_changed,
        'old_value', old_value,
        'new_value', new_value,
        'performed_by', performed_by
    ) AS metadata_json
FROM lead_audit_log

UNION ALL

SELECT
    id,
    lead_id,
    'tag'::text AS activity_type,
    created_at AS activity_timestamp,
    'Tag linked: ' || tag_id::text AS summary,
    jsonb_build_object(
        'tag_id', tag_id
    ) AS metadata_json
FROM lead_tag_link

UNION ALL

SELECT
    id,
    lead_id,
    'score'::text AS activity_type,
    created_at AS activity_timestamp,
    'Score recorded: ' || score_value::text AS summary,
    jsonb_build_object(
        'score_value', score_value,
        'score_reason', score_reason,
        'model_version', model_version
    ) AS metadata_json
FROM lead_score

UNION ALL

SELECT
    id,
    lead_id,
    'score_history'::text AS activity_type,
    changed_at AS activity_timestamp,
    'Score changed: ' || coalesce(previous_score::text, 'null') ||
        ' -> ' || new_score::text AS summary,
    jsonb_build_object(
        'previous_score', previous_score,
        'new_score', new_score,
        'change_reason', change_reason,
        'model_version', model_version
    ) AS metadata_json
FROM lead_score_history

UNION ALL

SELECT
    id,
    lead_id,
    'webhook'::text AS activity_type,
    created_at AS activity_timestamp,
    'Webhook attempt #' || attempt_number::text || ' to ' || target_url ||
        coalesce(' (status ' || response_status::text || ')', '') AS summary,
    jsonb_build_object(
        'target_url', target_url,
        'payload_json', payload_json,
        'response_status', response_status,
        'response_body', response_body,
        'attempt_number', attempt_number
    ) AS metadata_json
FROM lead_webhook_event

UNION ALL

SELECT
    id,
    source_lead_id AS lead_id,
    'merge'::text AS activity_type,
    created_at AS activity_timestamp,
    'Merged into ' || target_lead_id::text ||
        coalesce(': ' || merge_reason, '') AS summary,
    jsonb_build_object(
        'source_lead_id', source_lead_id,
        'target_lead_id', target_lead_id,
        'merge_reason', merge_reason,
        'performed_by', performed_by
    ) AS metadata_json
FROM lead_merge_history
WITH NO DATA;
"""


DROP_VIEW_SQL = "DROP MATERIALIZED VIEW IF EXISTS lead_activity_timeline;"


def upgrade() -> None:
    op.execute(CREATE_VIEW_SQL)
    op.execute("CREATE INDEX ix_lead_activity_timeline_lead_id ON lead_activity_timeline (lead_id);")
    op.execute(
        "CREATE INDEX ix_lead_activity_timeline_activity_timestamp ON lead_activity_timeline (activity_timestamp DESC);"
    )
    op.execute("REFRESH MATERIALIZED VIEW lead_activity_timeline;")


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_lead_activity_timeline_activity_timestamp;")
    op.execute("DROP INDEX IF EXISTS ix_lead_activity_timeline_lead_id;")
    op.execute(DROP_VIEW_SQL)
