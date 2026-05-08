# LeadsForge

LeadsForge is a lead generation platform seed repository.

**Layout:** `backend/` (FastAPI + Poetry), `frontend/` (React + Vite + TypeScript), `contracts/` (shared API definitions).

## CI

GitHub Actions runs on every push and pull request:

- **backend:** `ruff check`, `ruff format --check`, `pytest`
- **frontend:** `eslint`, `vite build`

## Local development

### Backend

```bash
cd backend
poetry install
cp .env.example .env   # then edit DATABASE_URL (never commit .env)
poetry run uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: `http://127.0.0.1:8000/docs`

### Frontend

```bash
cd frontend
npm install
cp .env.example .env.local   # optional: set VITE_API_BASE_URL
npm run dev
```

Default API base is `http://127.0.0.1:8000`. Override with `VITE_API_BASE_URL` in `.env.local`.