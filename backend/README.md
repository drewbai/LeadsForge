# LeadsForge Backend

FastAPI service managed with **Poetry**.

## Setup

```bash
poetry install
cp .env.example .env
```

Put `DATABASE_URL` in `.env` (see `.env.example`). Do **not** commit `.env`.

## Run

```bash
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

## Tests & lint (from `backend/`)

```bash
poetry run pytest
poetry run ruff check .
poetry run ruff format .
```
