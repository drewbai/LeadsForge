"""Expose build/version metadata for the About UI."""

from __future__ import annotations

import os
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/about", tags=["about"])


@lru_cache(maxsize=1)
def _poetry_version_from_pyproject() -> str:
    backend_root = Path(__file__).resolve().parents[3]
    pyproject = backend_root / "pyproject.toml"
    try:
        with pyproject.open("rb") as f:
            data: dict[str, Any] = tomllib.load(f)
        tool = data.get("tool")
        if not isinstance(tool, dict):
            return "unknown"
        poetry = tool.get("poetry")
        if not isinstance(poetry, dict):
            return "unknown"
        ver = poetry.get("version")
        return str(ver) if ver is not None else "unknown"
    except OSError:
        return "unknown"


@router.get("/")
async def about_meta() -> dict[str, Any]:
    commit = os.environ.get("LEADSFORGE_GIT_COMMIT", "").strip() or None
    return {
        "backend_poetry_version": _poetry_version_from_pyproject(),
        "git_commit": commit,
    }
