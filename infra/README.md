# Infrastructure Roadmap

## Planned Structure
The infrastructure surface is being carved out to consolidate environment definitions and delivery automation. Target folders include:

- `terraform/` – Environment modules for staging, production, and ephemeral preview stacks.
- `pulumi/` – Optional TypeScript infrastructure code for experimental services and internal tooling.
- `kubernetes/` – Helm charts and manifests for long-running services (backend API, automation workers, frontend SSR).
- `db/` – Managed database configuration, Drizzle migration bundles, and seed coordination.
- `observability/` – OpenTelemetry collector configs, Grafana dashboards, alerting rules.
- `ci/` – Shared GitHub Actions, reusable workflows, and pipeline templates consumed by application repos.

## Next Steps
- Inventory existing deployment scripts (see `docs/DEPLOYMENT_GUIDE.md`) and translate them into reproducible Terraform modules.
- Decide whether Supabase remains the managed control plane or migrates to self-hosted Postgres inside the Kubernetes stack.
- Coordinate with the automation team so job schedulers and queues (Redis, Supabase, etc.) are provisioned via code instead of ad-hoc scripts.
