Memora MVP Grafana Monitoring Pack

Copy the files to the root of memora_final_project. It adds a separate monitoring-compose.yml and monitoring/ folder without replacing the main docker-compose.yml.

Start application API on 0.0.0.0:8000 and frontend on 0.0.0.0:5173, and ensure database service ports 5433, 7687, 6333, and 6379 are published on the host.

From project root run:
  docker compose -f monitoring-compose.yml up -d

Grafana: http://localhost:3000  user: admin  initial password: MemoraGrafana@2026
Prometheus: http://localhost:9090
Blackbox exporter: http://localhost:9115
Dashboard is provisioned automatically: Memora / Memora MVP Overview.

This dashboard monitors frontend/API HTTP availability and response probe duration/status, plus TCP reachability of PostgreSQL, Neo4j, Qdrant and Redis. It does not yet expose detailed application request counters, latency histograms, model latency/token usage or worker queue metrics because the current app package does not include an instrumented /metrics endpoint. Change the Grafana password after first login. These are local demo credentials only.
