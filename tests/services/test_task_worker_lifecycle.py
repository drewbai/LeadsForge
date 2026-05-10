"""Tests for the task-worker lifecycle hooks wired in app.main.

Covers the three contracts:
1. The kill-switch env var (``LEADSFORGE_DISABLE_TASK_WORKER``) suppresses
   worker startup. The conftest sets this for the entire test session, so
   without an explicit override the startup hook must be a no-op.
2. When enabled, startup creates a named asyncio Task on ``app.state``
   bound to a stop event.
3. Shutdown sets the stop event and awaits the task within the timeout.
"""

from __future__ import annotations

import asyncio

import pytest
from app import main as app_main
from app.main import (
    TASK_WORKER_DISABLE_ENV,
    _shutdown_task_worker,
    _startup_task_worker,
    app,
)


async def _force_clean_app_state() -> None:
    """Reset worker state between tests so each test starts from a clean slate."""
    app.state.task_worker_stop_event = None
    app.state.task_worker_task = None


@pytest.mark.asyncio
async def test_startup_is_noop_when_disabled(monkeypatch) -> None:
    monkeypatch.setenv(TASK_WORKER_DISABLE_ENV, "1")
    await _force_clean_app_state()

    await _startup_task_worker()

    assert getattr(app.state, "task_worker_task", None) is None
    assert getattr(app.state, "task_worker_stop_event", None) is None


@pytest.mark.asyncio
async def test_startup_creates_named_worker_task_when_enabled(monkeypatch) -> None:
    monkeypatch.setenv(TASK_WORKER_DISABLE_ENV, "0")
    await _force_clean_app_state()

    async def fake_loop(*, poll_interval_seconds, batch_size, stop_event):
        # Cooperative loop that exits cleanly when stop_event fires; mirrors
        # the production loop's stop_event semantics without touching the DB.
        while not stop_event.is_set():
            await asyncio.sleep(0.01)

    monkeypatch.setattr(app_main, "run_worker_loop", fake_loop)

    await _startup_task_worker()
    try:
        worker_task = app.state.task_worker_task
        stop_event = app.state.task_worker_stop_event

        assert isinstance(worker_task, asyncio.Task)
        assert worker_task.get_name() == "leadsforge-task-worker"
        assert not worker_task.done()
        assert isinstance(stop_event, asyncio.Event)
        assert not stop_event.is_set()
    finally:
        await _shutdown_task_worker()


@pytest.mark.asyncio
async def test_shutdown_sets_stop_event_and_awaits_task(monkeypatch) -> None:
    monkeypatch.setenv(TASK_WORKER_DISABLE_ENV, "0")
    await _force_clean_app_state()

    async def fake_loop(*, poll_interval_seconds, batch_size, stop_event):
        while not stop_event.is_set():
            await asyncio.sleep(0.01)

    monkeypatch.setattr(app_main, "run_worker_loop", fake_loop)

    await _startup_task_worker()
    worker_task = app.state.task_worker_task
    assert worker_task is not None and not worker_task.done()

    await _shutdown_task_worker()

    assert worker_task.done()
    assert getattr(app.state, "task_worker_task", None) is None
    assert getattr(app.state, "task_worker_stop_event", None) is None


@pytest.mark.asyncio
async def test_shutdown_cancels_worker_when_loop_ignores_stop_event(monkeypatch) -> None:
    monkeypatch.setenv(TASK_WORKER_DISABLE_ENV, "0")
    monkeypatch.setattr(app_main, "TASK_WORKER_SHUTDOWN_TIMEOUT_SECONDS", 0.1)
    await _force_clean_app_state()

    async def hung_loop(*, poll_interval_seconds, batch_size, stop_event):
        # Intentionally never observes stop_event — exercises the timeout/cancel branch.
        while True:
            await asyncio.sleep(0.05)

    monkeypatch.setattr(app_main, "run_worker_loop", hung_loop)

    await _startup_task_worker()
    worker_task = app.state.task_worker_task
    assert worker_task is not None

    await _shutdown_task_worker()

    assert worker_task.done()
    assert worker_task.cancelled()


@pytest.mark.asyncio
async def test_shutdown_is_safe_when_startup_was_skipped() -> None:
    """If startup never ran (or was disabled), shutdown must be a no-op, not raise."""
    await _force_clean_app_state()

    await _shutdown_task_worker()  # must not raise


def test_kill_switch_env_var_constant_matches_documented_name() -> None:
    """Guard: the constant must stay aligned with the public env-var name documented
    in the conftest comment and any future ops runbook."""
    assert TASK_WORKER_DISABLE_ENV == "LEADSFORGE_DISABLE_TASK_WORKER"
