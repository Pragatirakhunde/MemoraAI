# Memora MLOps patch notes

## Added
- Prometheus HTTP request metrics + `/metrics` endpoint.
- Separate Celery worker task metrics on port `9808`.
- Prometheus/Grafana monitoring-only compose file with persistent volumes, provisioned data source, dashboard and alerts.
- SHAP/LIME project-authorized CodeMind retrieval explanation endpoint and UI button.
- Qdrant Cloud URL/API-key support while preserving local host/port support.
- Backend/frontend Dockerfiles, `.dockerignore`, Render blueprint starter and GitHub Actions CI workflow.
- MLOps/deployment operations guide.

## Do not confuse implementation with final runtime verification
This package has not been deployed to Render and cannot verify a real GitHub delivery without your remote repository, public endpoint and secrets. After applying the patch, run backend tests, `npm run build`, verify Prometheus targets, and push a test commit to confirm the index update reaches CodeMind.
