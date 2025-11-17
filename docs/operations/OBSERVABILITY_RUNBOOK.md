# Observability Runbook

This runbook explains how to follow a request or agent action end-to-end now that correlation IDs, traces, and KPI metrics are published to Grafana/Loki/Tempo.

## 1. Required services

1. Start the observability stack from the repository root:
   ```bash
   docker compose -f observability/docker-compose.yml up -d
   ```
2. Confirm the default datasources (Prometheus, Loki, Tempo/OTLP collector) are healthy in Grafana at `http://localhost:3000` (user/pass: `admin/admin`).

## 2. Backend API tracing + metrics

* Every Express request now carries a `correlationId` (middleware) and emits:
  * Structured logs to console + Loki (`LOKI_URL=http://localhost:3100`).
  * OTLP traces to the collector (`OTEL_COLLECTOR_ENDPOINT=http://localhost:4318/v1/traces`).
  * Prometheus metrics exposed at `http://<api-host>/metrics` (request counters, latency histograms, `flowstate_kpi_value`).
* **Environment variables**:
  * `BYPASS_AUTH_TOKEN` – shared secret for CI/Cypress/API smoke tests.
  * `OTEL_SERVICE_NAME`, `LOKI_URL`, `OTEL_COLLECTOR_ENDPOINT` – optional overrides per environment.
* **Verification**:
  1. Call any API (e.g. `GET /api/kpis?category=executive` with the bearer bypass token).
  2. Use Grafana Explore → Loki datasource, query `{service="flowstate-ai-backend"} |= "correlationId"` to find the log line.
  3. Copy the `trace_id` and open Tempo/Jaeger view from the same log entry for the span timeline.
  4. Prometheus scrape target: add `http://backend:3001/metrics` and watch `flowstate_http_request_duration_seconds` + `flowstate_kpi_value`.

## 3. Python worker + agent actions

* A new observability client publishes every agent action to Loki + OTLP via `python-worker/evolution_framework/observability.py`.
* Synthetic load tests can be enabled by setting:
  ```bash
  export ENABLE_SYNTHETIC_LOAD_TESTS=true
  export EVOLUTION_DATABASE_URL=postgresql://<user>:<pass>@<host>:5432/flowstate
  ```
  When the FastAPI worker boots it spins up the `SyntheticLoadScheduler`, generates 100k synthetic tasks per interval, and pushes bottleneck reports into `PerformanceTuner` + `CostOptimizer` (see Loki label `service=flowstate-ai-python-worker`).
* Logs include `correlation.id` attributes so backend ↔ worker traces can be correlated with the same ID.

## 4. KPI dashboards

* Grafana Prometheus datasource now exposes `flowstate_kpi_value{category="executive",name="Monthly Active Users"}`.
* Build dashboards:
  1. Panel type: Stat → query `flowstate_kpi_value{category="business"}`.
  2. Use `Legend: {{name}} ({{category}})` and `Reduce → last not null` to show the latest KPI snapshot.

## 5. Synthetic load troubleshooting

* Check `python-worker` logs for `Synthetic load scheduler started`.
* Verify Prometheus metric `flowstate_http_requests_total` is increasing while scheduler runs.
* To pause the loop, set `ENABLE_SYNTHETIC_LOAD_TESTS=false` and restart the worker or call the FastAPI shutdown hook.

## 6. CI enforcement

* `.github/workflows/test.yml` blocks merges until backend Jest, frontend Vitest, python PyTest, Playwright, and Cypress jobs pass.
* Bypass tokens for CI are injected via `BYPASS_AUTH_TOKEN=e2e-bypass-token`. Local smoke tests must export the same token before running Cypress or Playwright suites.
