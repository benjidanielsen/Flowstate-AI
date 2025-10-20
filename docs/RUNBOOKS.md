# Flowstate-AI Deployment Runbooks

This document provides deployment-ready runbooks for operating the Flowstate-AI platform in production environments. Each runbook contains the objectives, required tooling, and step-by-step procedures to execute common operational tasks.

---

## Security Response Runbook

**Objective:** Quickly respond to authentication, authorization, or data-protection incidents.

### Preparation
- Ensure `JWT_SECRET`, `JWT_ISSUER`, and `JWT_AUDIENCE` are stored in a hardened secret manager (e.g., AWS Secrets Manager, HashiCorp Vault).
- Maintain a rotation schedule for signing keys and Redis session secrets (`REDIS_URL`, `REDIS_CACHE_URL`).
- Configure audit logging sinks (e.g., CloudWatch, ELK, Datadog) that receive backend logs.
- Document privileged roles (`admin`, `manager`, `analyst`, `agent`, `integration`, `service`) and map them to business owners.

### Incident Validation
1. Trigger the `/api/health` and `/api/ready` endpoints to confirm service availability.
2. Review authentication logs for suspicious `403` or session mismatch entries (look for `Authentication failed` events in backend logs).
3. Inspect Prometheus metrics `http_requests_errors_total` filtered by role-restricted routes to detect spikes.
4. Verify Redis session integrity using the session management utility (`backend/src/utils/sessionManager.ts`).

### Response Actions
1. **Revoke tokens** – use the session manager CLI/script to delete active sessions for compromised users (`deleteUserSessions`).
2. **Rotate secrets** – update JWT signing keys and Redis credentials; restart backend pods with new environment variables.
3. **Tighten RBAC** – adjust route-level role bindings in `backend/src/routes/index.ts` if temporary lockdown is required.
4. **Communicate** – notify affected stakeholders with a summary of impacted users, actions taken, and next steps.

### Post-Incident Checklist
- Capture timelines and attach relevant Prometheus graphs, Redis logs, and audit entries.
- File follow-up engineering tasks (e.g., add tests, extend monitoring coverage) in the incident tracking system.
- Schedule a key rotation rehearsal within the next sprint if gaps were observed.

---

## Monitoring & Observability Runbook

**Objective:** Maintain visibility into service health using Prometheus and OpenTelemetry.

### Preparation
- Deploy a Prometheus-compatible scraper that targets:
  - Backend: `http://<backend-host>:3001/api/metrics`
  - Worker: `http://<worker-host>:8000/metrics`
- Configure the OTLP collector endpoint (default `http://localhost:4318/v1/traces`) and ensure both services have network access to it.
- Register dashboards for key metrics: request latency, active requests, error counts, workflow executions.

### Routine Checks
1. **Backend metrics** – verify `http_request_duration_seconds` and `http_requests_errors_total` for spikes. Correlate with `http_requests_active` to understand saturation.
2. **Worker metrics** – observe `worker_backend_request_duration_seconds`, `worker_backend_requests_total`, and `worker_agent_workflows_total` to ensure steady throughput.
3. **Tracing** – confirm that traces from both services arrive in the collector. Sampling rate can be tuned via OTEL environment variables.
4. **Health endpoints** – schedule synthetic checks for `/api/health`, `/api/ready`, `/health`, and `/metrics` endpoints.

### Troubleshooting Workflow
1. If latency increases:
   - Inspect cache hit rates in Redis (vector cache namespace `vector-search:*`).
   - Evaluate slow SQL logs (`match_documents` calls) and consider lowering limits/thresholds temporarily.
2. If trace export fails:
   - Ensure OTEL environment flags (`OTEL_ENABLED`, `OTEL_EXPORTER_OTLP_ENDPOINT`) are correctly set.
   - Restart services to reinitialize the SDKs after collector outages.
3. For missing metrics:
   - Confirm Prometheus targets are `UP` and TLS certificates (if any) remain valid.
   - Validate that middleware instrumentation (`backend/src/middleware/performanceMiddleware.ts` and `python-worker/src/instrumentation.py`) has not been bypassed by route changes.

### Escalation
- If production KPIs degrade, page the on-call engineer and provide links to dashboards, traces, and recent deployment diffs.
- Engage the data/ML team when vector search accuracy drops or recommendation quality is questioned.

---

## Scaling & Performance Runbook

**Objective:** Scale services horizontally or vertically to maintain SLOs.

### Capacity Planning Inputs
- Backend API throughput and 95th percentile latency (`http_request_duration_seconds{quantile="0.95"}`)
- Redis cache hit ratio and memory usage for session + vector caches
- Worker CPU utilization and workflow backlog size (from `worker_agent_workflows_total` trends)

### Horizontal Scaling
1. **Backend service**
   - Increase replica count in the orchestration platform (Kubernetes `Deployment`, ECS service, etc.).
   - Ensure each replica has access to shared Redis and Postgres resources.
   - After scaling, re-check `/api/ready` and confirm Prometheus scrapes all replicas.
2. **Worker service**
   - Scale worker instances based on queue depth or workflow counter velocity.
   - Run `POST /agents/workflows/customer-insights` against each instance to verify orchestration readiness.

### Vertical Scaling
- If CPU-bound, adjust container resource limits and restart pods.
- For memory pressure (e.g., large vector results), increase container memory and update Node.js heap settings (`--max-old-space-size`).
- Consider increasing Redis cache TTL or shard size if eviction occurs frequently.

### Performance Tuning
- Utilize Redis caching for vector search (`backend/src/cache/vectorSearchCache.ts`) and monitor TTL effectiveness.
- Adjust vector search thresholds/limits via API parameters to throttle expensive queries when under load.
- Enable feature flags or rate limiting in the API gateway during extreme spikes.

### Verification Checklist
- Confirm autoscaling policies are restored to normal thresholds after manual overrides.
- Update runbooks with new capacity baselines and share lessons learned with the platform team.

---

## Reference
- Backend Observability: `backend/src/utils/metrics.ts`, `backend/src/utils/tracer.ts`
- Worker Observability: `python-worker/src/instrumentation.py`
- Specialized Agents & Orchestration: `python-worker/app/agents/`
- Vector Cache Implementation: `backend/src/cache/`
