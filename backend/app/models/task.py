from datetime import datetime, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.types import TypeEngine

from app.db.base import Base

TASK_STATUS_PENDING = "pending"
TASK_STATUS_RUNNING = "running"
TASK_STATUS_SUCCESS = "success"
TASK_STATUS_ERROR = "error"


VALID_TASK_STATUSES: frozenset[str] = frozenset(
    {
        TASK_STATUS_PENDING,
        TASK_STATUS_RUNNING,
        TASK_STATUS_SUCCESS,
        TASK_STATUS_ERROR,
    }
)


# JSON on every dialect; JSONB only when the bind is PostgreSQL.
# Keeps SQLite (used by the CI test harness) happy without losing JSONB in prod.
_JSON_PORTABLE: TypeEngine[Any] = JSON().with_variant(JSONB(), "postgresql")


class Task(Base):
    __tablename__ = "task"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    task_type: Mapped[str] = mapped_column(String, nullable=False, index=True)
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default=TASK_STATUS_PENDING,
        index=True,
    )
    payload: Mapped[dict[str, Any]] = mapped_column(
        _JSON_PORTABLE,
        nullable=False,
        default=dict,
    )
    result: Mapped[dict[str, Any] | None] = mapped_column(_JSON_PORTABLE, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )


def serialize_task(task: Task) -> dict[str, Any]:
    return {
        "id": str(task.id),
        "task_type": task.task_type,
        "status": task.status,
        "payload": task.payload,
        "result": task.result,
        "error_message": task.error_message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "updated_at": task.updated_at.isoformat() if task.updated_at else None,
        "started_at": task.started_at.isoformat() if task.started_at else None,
        "finished_at": task.finished_at.isoformat() if task.finished_at else None,
    }
