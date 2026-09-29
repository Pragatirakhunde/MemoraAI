# CodeMind Setup

## 1. Database

Run from `backend`:

```powershell
alembic upgrade head
alembic current
```

The Phase 16 migration adds:

- `code_repositories`
- `code_files`
- `code_symbols`
- `code_chunks`
- `code_commits`

## 2. Dependencies

The backend requirements include optional Tree-sitter grammars for Python, JavaScript, TypeScript and TSX. The parser uses Python AST for Python and a conservative JavaScript/TypeScript extractor with a Tree-sitter syntax-validation path when the grammar packages are available.

## 3. Create a repository source

Use the admin CodeMind screen or:

```http
POST /api/v1/codemind/repositories
```

Example local repository:

```json
{
  "project_id": 1,
  "name": "PayFlow Codebase",
  "provider": "local",
  "local_path": "../datasets/technova/payflow",
  "default_branch": "main"
}
```

## 4. Validate and index

```http
POST /api/v1/codemind/repositories/{repository_id}/validate
POST /api/v1/codemind/repositories/{repository_id}/index
```

Indexing updates PostgreSQL, the `codemind_code_chunks` Qdrant collection and the CodeMind Neo4j graph.

## 5. Project-scoped queries

All query endpoints use `require_project_access`. Never pass an untrusted project id through to retrieval without server-side authorization.

Available query capabilities include:

- semantic code search
- CodeMind answers
- architecture summary
- dependency/call analysis
- impact analysis
- Git history
- business-rule-to-code retrieval
- similar-code search

## 6. GitHub

For GitHub repositories, configure `GITHUB_WEBHOOK_SECRET`. The webhook validates `X-Hub-Signature-256` and queues incremental repository indexing through Celery.
