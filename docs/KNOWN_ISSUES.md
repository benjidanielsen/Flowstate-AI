# Known Issues and Follow-up Tasks

This document tracks outstanding gaps after the security/observability/agent rollout.

## Backend
- **Jest dependency resolution:** `npm test -- --runTestsByPath src/tests/vectorSearch.test.ts` fails because the repository tracks a partial `node_modules` tree without `cliui` build artifacts. Regenerate the package (`npm install cliui@^8`) or rehydrate the tracked files before running the suite.
- **Vector cache coverage:** Add Redis-backed integration tests for `backend/src/services/vectorSearchService.ts`, especially the `invalidateVectorCache` pathways, to verify cache coherence.

## Python Worker
- **Legacy test suite:** Only `PYTHONPATH=. pytest tests/test_app_agents.py` succeeds. Remaining tests import evolution components that require heavy dependencies such as `sentence_transformers`. Either add the dependency or provide lightweight shims/skips.
- **Workflow endpoint coverage:** Implement API-level tests for the new `/agents/workflows/customer-insights` route and instrumentation plumbing in `python-worker/src/main.py` (around the workflow router wiring).
- **Prometheus validation:** Add end-to-end scrape checks to confirm the Prometheus exporter in `python-worker/src/instrumentation.py` exposes metrics after startup.

## Infrastructure
- **Redis availability:** Create health or smoke tests that cover cache connectivity, ensuring `REDIS_URL` and `REDIS_CACHE_URL` endpoints are reachable from both backend and worker containers.
