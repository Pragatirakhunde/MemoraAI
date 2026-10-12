# Memora MLOps implementation and acceptance guide

## Scope in this patch

- Prometheus API metrics at `GET /metrics`.
- Separate Celery-worker metrics endpoint at port `9808`.
- Grafana provisioning with a Memora dashboard and Prometheus scrape configuration.
- Alert rules for API/worker unavailability, sustained HTTP 5xx rate and CodeMind indexing failures.
- Counters for indexed files, changed/skipped/deleted files, symbols, chunks and commit updates.
- SHAP and LIME explain the effect of query terms on BGE-M3 similarity to one authorized CodeMind result. They do **not** explain Gemini's hidden reasoning and are not evidence of causality.
- GitHub Actions runs backend syntax/tests and a frontend production build on pushes/PRs.
- Dockerfiles for API/worker and the frontend, plus a Render blueprint starter.

## Local setup

1. Apply the patch to the current project, preserving `.env` files and local data.
2. Install backend runtime dependencies and optional explainability dependencies:
   `python -m pip install -r backend/requirements.txt -r backend/requirements-mlops.txt`
3. Run the API on port 8000 and the Celery worker using the existing commands. The worker serves metrics on port 9808.
4. Set a strong local Grafana password and start only the monitoring stack, not the existing data stack:
   PowerShell: `$env:GRAFANA_ADMIN_PASSWORD = "use-a-strong-local-password"`
   `docker compose -f docker-compose.monitoring.yml up -d`
5. Open `http://localhost:9090/targets` and confirm `memora-api` and `memora-celery-worker` are UP.
6. Open `http://localhost:3000`, sign in using username `admin` and the password you set, and open **Memora MLOps / Runtime Health**.

Because Prometheus/Grafana are containers while the API and worker run on the Windows host, the configured targets use `host.docker.internal`. If the application runs inside Docker instead, change Prometheus targets to the Compose service DNS names and container ports.

## SHAP + LIME usage

In Employee CodeMind, select a project, run a semantic code search, and click **Explain relevance (SHAP + LIME)** on a result. The API re-runs the search under the same backend project authorization, selects the result rank, perturbs query terms, and measures BGE-M3 similarity against that candidate. Positive/negative contributions are local model-agnostic attributions; they are not guaranteed causal effects.

Install `backend/requirements-mlops.txt` to enable this endpoint. Explanation is compute-intensive, so use it for debugging/evaluation rather than every production search request.

## GitHub automation flow

GitHub push -> signature/repository/branch validation -> Celery task queued -> source checkout/update -> checksum-based incremental code indexing -> Qdrant/Neo4j updates -> Git history visible in CodeMind. Normal pushes update the index; they do not retrain BGE-M3 or Gemini.

A GitHub-backed repository record is required. A row with `provider=local` and blank `remote_url` will return `404 Active GitHub repository not found` for webhook delivery. Configure a real `github` provider and remote URL in Admin before adding the webhook. Use an HTTPS public backend URL. Set the same `GITHUB_WEBHOOK_SECRET` in Memora and GitHub; do not commit it.

## Deployment with Render

The `render.yaml` file is a starter blueprint for the backend API, Celery worker, managed PostgreSQL/Key Value and static frontend. The API service runs `alembic upgrade head` as a pre-deploy command, so schema migrations occur once from the API service rather than concurrently from both API and worker. It intentionally asks for secret values through the dashboard. It expects **external Qdrant Cloud and Neo4j Aura** endpoints for persistence; `QDRANT_URL`/`QDRANT_API_KEY` are supported by this patch. Before launch:

1. Push the project to a GitHub repository with secrets removed.
2. Create Qdrant Cloud and Neo4j Aura resources and enter their endpoints/credentials as Render environment variables.
3. Add the Gemini API key, GitHub webhook secret/token and set frontend `VITE_API_URL` to the deployed API base URL ending in `/api/v1`.
4. Set backend `CORS_ORIGINS` to the exact deployed frontend origin, e.g. `https://your-frontend.onrender.com` (no trailing `/api/v1`).
5. Confirm API and worker use the same JWT/environment secrets. Verify health/migrations before seeding demo data.
6. The BGE-M3 model is relatively large; choose enough memory for model loading and indexing. Small/free plans may restart/OOM or be too slow. Hosted services/compute may incur cost.
7. Do not deploy the local Windows path used for PayFlow. Configure a GitHub repository URL for deployed CodeMind indexing because local paths on your machine do not exist in the cloud.

This is deployment scaffolding, not a deployment already performed. The included Prometheus/Grafana Compose stack is for local/demo monitoring; the Render blueprint does not provision hosted Prometheus/Grafana, so production monitoring would require Grafana Cloud or separately deployed, secured monitoring services. Actual deploy requires the project's GitHub remote, cloud accounts and secrets.
