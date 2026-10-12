# Memora update patch — Git history, GitHub push sync, and formatted AI answers

## Included changes

- GitHub webhooks validate `X-Hub-Signature-256`, the configured repository identity, and the configured branch before queueing a Celery refresh.
- The endpoint acknowledges matching push events with `status: queued`, records a pending index state before dispatch, and records enqueue/indexing failures in the repository status.
- GitHub checkout fetches keep a configurable recent commit history window (`CODEMIND_GIT_HISTORY_DEPTH`, default 100) instead of depth 1.
- Commit indexing records changed paths and additions/deletions. The Git history API/UI expose these fields.
- Code indexing remains checksum-based: unchanged files are skipped, changed/new files are embedded using the existing pretrained embedding model, and removed files are removed from the active index. No model training/fine-tuning is run on a push.
- Optional `GITHUB_TOKEN` supports HTTPS access to private GitHub repositories. Leave blank for public repos. Do not put the token into the saved `remote_url`.
- AI Assistant's generation prompt asks for well-structured Markdown. The frontend safely renders headings, paragraphs, bullets/numbered lists, tables, quotes, links, inline code and fenced code blocks without injecting raw HTML. CodeMind answers use the same formatting.
- Added webhook helper tests and setup documentation.

## Apply safely

Extract this patch ZIP into the existing `memora_final_project` directory and allow files to overwrite. It contains only source, documentation, tests and `.env.example` files; it does not contain `.env`, database files, `.venv`, or `node_modules`.

No database migration is required by this patch because it reuses the existing `code_commits` table and its `additions` / `deletions` fields.

After applying:

1. Add `GITHUB_WEBHOOK_SECRET` (and `GITHUB_TOKEN` only if needed) to `backend/.env`.
2. Restart FastAPI and the Celery worker.
3. Run the backend syntax checks and `python -m pytest -q tests/test_github_webhook.py`.
4. Configure GitHub **Settings → Webhooks** for `https://YOUR_PUBLIC_HOST/api/v1/codemind/webhook/github/REPOSITORY_ID`, JSON content type, the same secret, and push events only. GitHub cannot reach a local-only `localhost` URL.
5. Push a small code change to the configured branch and confirm the delivery response is queued, worker logs show a refresh, repository status returns to completed, the new commit appears under CodeMind Git history, and the changed code is searchable.

## Verification performed for this patch

- Python `compileall` over `app`, `scripts`, and `tests`: passed.
- Webhook helper unit tests: 4 passed.
- Local Git connector smoke test: successfully synchronized a checkout from 3 to 4 commits and fetched the newly added file.
- AI prompt-format instruction check: passed.
- Modified TSX files passed TypeScript syntax transpilation.

Full Vite production build and real GitHub webhook delivery were not verified in this environment. The npm dependency install timed out here, and a real GitHub delivery requires a reachable HTTPS endpoint plus your configured secret/token and running Redis/Celery services.
