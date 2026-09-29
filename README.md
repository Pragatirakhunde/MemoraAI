# Memora AI — Enterprise Organizational Memory + CodeMind

Memora is an organization-memory platform with a project-scoped CodeMind module.

## Product areas

- Organizational Memory and AI Assistant
- Project and member authorization
- Data-source sync and document RAG
- Qdrant vector retrieval
- Neo4j knowledge graph
- CodeMind semantic code search and code understanding
- Admin management and Employee workspace

## Runtime architecture

Frontend: React + TypeScript + Vite
Backend: FastAPI + SQLAlchemy + Alembic
Databases: PostgreSQL + Neo4j + Qdrant
Background: Celery + Redis
AI: Gemini API
Embeddings: BGE-M3

## Setup

1. Copy `.env.example` to `.env` and fill in the required credentials.
2. Start PostgreSQL, Neo4j, Qdrant and Redis:

```powershell
docker compose up -d
```

3. Backend:

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
alembic upgrade head
```

4. Create demo accounts/data after the database is initialized:

```powershell
python scripts/setup_demo.py
```

5. Start FastAPI:

```powershell
uvicorn app.main:app --reload
```

6. Start the Celery worker in another terminal:

```powershell
celery -A app.workers.celery_app:celery_app worker --loglevel=INFO --pool=solo
```

7. Start Celery Beat when scheduled background sync is required:

```powershell
celery -A app.workers.celery_app:celery_app beat --loglevel=INFO
```

8. Frontend:

```powershell
cd frontend
copy .env.example .env
npm ci
npm run dev
```

The frontend expects `VITE_API_URL=http://127.0.0.1:8000/api/v1` by default.

## CodeMind

Admin creates a repository source for an active project, validates it, and indexes it. Employees see only projects returned by `/projects/my` and every CodeMind API is protected by the existing server-side project authorization dependency.

Local repository example:

```text
../datasets/technova/payflow
```

CodeMind indexes supported source files, extracts symbols/imports/calls, stores code chunks in PostgreSQL, embeds them into a project-scoped Qdrant collection, and mirrors repository/file/symbol relationships into Neo4j.

## Demo credentials

The seed scripts create:

- Admin: `admin@technova.com` / `Admin@123`
- Employee: `employee@technova.com` / `Employee@123`

Change these credentials for any real deployment.

## Validation

Backend syntax:

```powershell
python -m compileall app scripts
```

Database migration:

```powershell
alembic current
alembic check
```

Frontend build:

```powershell
npm run build
```

## Important

External services still require their own runtime availability and credentials: PostgreSQL, Neo4j, Qdrant, Redis and a valid Gemini API key.
