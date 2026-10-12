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

## 7. Git history and incremental indexing

Git history requires the repository directory to contain Git metadata (`.git`). The included TechNova PayFlow directory inside a ZIP may not contain `.git`; in that case code can still be indexed, but there will be no commits to display. To demonstrate real history and automatic push updates, register a GitHub repository or point a `local` provider at an actual Git checkout.

CodeMind stores up to `CODEMIND_GIT_HISTORY_LIMIT` recent commits per repository (default `100`) in PostgreSQL. The checkout uses `CODEMIND_GIT_HISTORY_DEPTH` (default `100`) so a GitHub repository has a useful recent commit window without requiring unlimited history. Commit records include author, timestamp, message, changed paths, additions and deletions.

Repository indexing compares SHA-256 checksums for supported source files:

- Unchanged files are skipped and do not have embeddings regenerated.
- Changed/new files are parsed and their code chunks are embedded/upserted with the existing pretrained embedding model.
- Removed files have their active code chunks/vectors/symbols removed from the active index.
- New commit metadata is inserted; existing recent commit records have changed-file statistics refreshed.

This is embedding inference, **not model training or fine-tuning**.

## 8. Configure a GitHub push webhook

1. Create a GitHub CodeMind repository record from the Admin Center with provider `github`, its HTTPS/SSH remote URL, and the branch to watch.
2. Add these values to `backend/.env` and restart FastAPI and Celery after changing them:

```dotenv
GITHUB_WEBHOOK_SECRET=use-a-long-random-secret
GITHUB_TOKEN=
CODEMIND_GIT_HISTORY_DEPTH=100
CODEMIND_GIT_HISTORY_LIMIT=100
```

`GITHUB_WEBHOOK_SECRET` must exactly match the secret configured in the GitHub webhook. `GITHUB_TOKEN` is optional for public repositories; use a least-privilege token for private repositories with an HTTPS remote URL. SSH remotes need SSH credentials configured for the worker account. The token is passed to Git as a temporary environment config and is not inserted into the configured remote URL.

3. In the GitHub repository, open **Settings → Webhooks → Add webhook**:
   - Payload URL: `https://YOUR_PUBLIC_HOST/api/v1/codemind/webhook/github/REPOSITORY_ID`
   - Content type: `application/json`
   - Secret: the same value as `GITHUB_WEBHOOK_SECRET`
   - Events: **Just the push event**
   - Active: enabled
4. GitHub must be able to reach the payload URL. `localhost` / `127.0.0.1` is not reachable by GitHub; use an HTTPS deployment or an HTTPS development tunnel for testing.
5. Ensure Redis and a Celery worker are running. The endpoint verifies `X-Hub-Signature-256`, checks that the signed payload's repository matches the configured remote, checks `refs/heads/<default_branch>`, then returns `status: queued`. Other branches and unsupported events are ignored. Repository status changes to `pending`, then `running`, `completed` or `failed`.
6. Push a small change to the configured branch. Check GitHub **Settings → Webhooks → Recent Deliveries**, the Celery worker logs, Admin's repository status, and the CodeMind **Git history** panel. The delivery should return HTTP 200 with `status: queued` for a matching push.

The receiver intentionally doesn't require a user JWT because GitHub sends webhook requests. HMAC signature validation, repository identity matching and branch validation protect the endpoint. Do not expose the webhook secret or GitHub token in logs or screenshots.

## 9. Webhook endpoint

```http
POST /api/v1/codemind/webhook/github/{repository_id}
```

A matching push should respond with a queue acknowledgement similar to:

```json
{
  "status": "queued",
  "task_id": "<celery-task-id>",
  "repository_id": 1,
  "commit": "<new-commit-sha>",
  "message": "Repository refresh queued. Changed files are re-indexed; the embedding model is not retrained."
}
```

A queue acknowledgement means the work was enqueued, not that indexing has finished. Confirm the final `index_status` and `last_index_error` in the repository record/UI.
