# Ops Runbook

## Deploy
- Staging: Actions → `deploy-staging` → ref=`main`
- Production: Actions → `deploy-prod` → tag=`vX.Y.Z`

## Migrations
- Actions → `migrate` → target=`staging|production`
- SQL lives in `db/migrations/*.sql` with `-- migrate:up/down` sections.

## E2E
- Pull Requests trigger the `e2e` workflow via Playwright; download artifacts for traces when failures occur.

## Backups
- `backup-db` runs nightly; artifacts are retained for 14 days. Move them to long-term storage when possible.

## Observability
- OTEL traces, metrics, and logs emit to the local collector (`docker/otel-collector.yaml`). Integrate with Grafana Tempo/Prometheus/Loki for richer visibility.
