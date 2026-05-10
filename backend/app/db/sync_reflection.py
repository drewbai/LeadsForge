"""Synchronous metadata reflection helpers for use inside ``AsyncSession.run_sync``."""

from __future__ import annotations

from typing import cast

from sqlalchemy import MetaData
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


def reflect_bind(metadata: MetaData, sync_session: Session) -> None:
    """Populate ``metadata`` from the sync engine bound to the session."""
    bind = sync_session.get_bind()
    if bind is None:
        msg = "Cannot reflect metadata: session has no bind"
        raise RuntimeError(msg)
    # Stub surface expects ``Engine``; runtime bind is the async stack's engine.
    metadata.reflect(bind=cast(Engine, bind))
