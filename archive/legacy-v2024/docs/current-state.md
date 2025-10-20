# Flowstate-AI Current State Overview

## High-Level Architecture
Flowstate-AI is organized as a polyglot monorepo anchored around three production workloads:

- **TypeScript/Node.js backend** that exposes the CRM API surface, orchestrates background automation, and mediates all persistence integrations.
- **React/Vite frontend** that consumes the API and renders dashboards, workflows, and CRM tooling for operators.
- **Python automation worker** that implements AI-assisted decisioning, reminder scheduling, and evolution orchestration tasks in coordination with the backend.

The repository also contains auxiliary tooling (GitHub integration utilities, SQL bootstrap scripts, etc.) and living documentation that describe operating procedures and roadmap considerations.

## Module Inventory
### Backend (`backend/`)
The backend is an Express application that boots from `src/index.ts`, wiring middleware, OpenAPI documentation, and database initialization before mounting modular route bundles.【F:backend/src/index.ts†L1-L103】 The router aggregates feature areas such as customer management, interactions, KPIs, AI coordination, and vector search under `/api`, secured by shared authentication middleware.【F:backend/src/routes/index.ts†L1-L39】

Domain logic is decomposed into:
- **Controllers** under `src/controllers/` that translate HTTP input to service calls (e.g., `agentController.ts`, `authController.ts`, `vectorSearchController.ts`).【F:backend/src/controllers/agentController.ts†L1-L5】【F:backend/src/controllers/authController.ts†L1-L5】【F:backend/src/controllers/vectorSearchController.ts†L1-L5】
- **Services** under `src/services/` that encapsulate business workflows such as agent lifecycle management, AI coordination, memory storage, KPI analytics, and workflow orchestration.【F:backend/src/services/agentService.ts†L1-L6】【F:backend/src/services/aiCoordinationService.ts†L1-L7】【F:backend/src/services/workflowOrchestrationService.ts†L1-L7】
- **Middleware** for cross-cutting concerns like correlation IDs, idempotency, and performance telemetry.【F:backend/src/middleware/performanceMiddleware.ts†L1-L15】【F:backend/src/middleware/correlationId.ts†L1-L16】【F:backend/src/middleware/idempotency.ts†L1-L16】
- **Database access** via Drizzle ORM and Supabase helpers in `src/database/`, plus SQL seeds in `/create_*.sql` for schema bootstrap.【F:backend/src/database/index.ts†L1-L10】【F:backend/src/database/supabase.ts†L1-L12】【F:backend/create_agent_states.sql†L1-L14】
- **Utilities** for logging, OpenTelemetry tracing, and PII redaction in `src/utils/` to support observability and compliance.【F:backend/src/utils/logger.ts†L1-L14】【F:backend/src/utils/tracer.ts†L1-L25】【F:backend/src/utils/piiRedaction.ts†L1-L22】

The backend directory also houses auxiliary automation scripts (`auto_save.py`, `lead_generation.py`, etc.) and worker entry points (`websocket_server.py`, `conversion_tracking.py`) that integrate with the core API layer for specialized campaigns.【F:backend/auto_save.py†L1-L18】【F:backend/lead_generation.py†L1-L20】【F:backend/websocket_server.py†L1-L15】

### Frontend (`frontend/`)
The frontend is a Vite-powered React SPA bootstrapped from `src/main.tsx`, which mounts the router-aware `App.tsx` under an authentication provider.【F:frontend/src/main.tsx†L1-L12】【F:frontend/src/App.tsx†L1-L46】 Feature experiences are organized by responsibility:

- **Routing and state**: `App.tsx` defines protected routes for dashboards, AI logs, and KPIs guarded by `ProtectedRoute.tsx`, while `context/AuthContext.tsx` persists authentication state and session helpers.【F:frontend/src/components/ProtectedRoute.tsx†L1-L19】【F:frontend/src/context/AuthContext.tsx†L1-L37】
- **Pages**: Individual dashboards and workflows live in `src/pages/` (e.g., `Dashboard.tsx`, `Customers.tsx`, `EvolutionDashboard.tsx`, `QualificationForm.tsx`).【F:frontend/src/pages/Dashboard.tsx†L1-L5】【F:frontend/src/pages/Customers.tsx†L1-L5】【F:frontend/src/pages/EvolutionDashboard.tsx†L1-L5】【F:frontend/src/pages/QualificationForm.tsx†L1-L5】
- **Components**: Reusable UI building blocks and modals reside in `src/components/`, alongside domain-specific CRM dashboards and layout scaffolding.【F:frontend/src/components/Layout.tsx†L1-L5】【F:frontend/src/components/AddInteractionModal.tsx†L1-L5】【F:frontend/src/components/CRMDashboard.jsx†L1-L5】
- **Client services**: `src/services/api.ts` and `src/api/axiosInstance.ts` provide typed API accessors for CRM resources, AI coordination, reminders, and analytics.【F:frontend/src/services/api.ts†L1-L95】【F:frontend/src/api/axiosInstance.ts†L1-L21】
- **Hooks and contexts**: `src/hooks/useDebounce.ts` offers UI-friendly utilities, and `src/contexts/ToastContext.tsx` centralizes toast notifications.【F:frontend/src/hooks/useDebounce.ts†L1-L26】【F:frontend/src/contexts/ToastContext.tsx†L1-L31】

### Python Automation Worker (`python-worker/`)
The Python service is a FastAPI application hosted in `src/main.py`, exposing reminder scheduling, Next Best Action (NBA) analytics, and autonomous experimentation endpoints that proxy into the backend.【F:python-worker/src/main.py†L1-L108】 Supporting modules include:

- **Evolution Framework** (`evolution_framework/`) with orchestrators, anomaly detection, and self-modification primitives for AI experimentation.【F:python-worker/evolution_framework/self_modification_orchestrator.py†L1-L32】【F:python-worker/evolution_framework/anomaly_detector.py†L1-L27】【F:python-worker/evolution_framework/evolution_manager.py†L1-L21】
- **Domain services** such as `services/nba_service.py` and `services/reminder_service.py` that analyze CRM data for recommendations and reminder workflows.【F:python-worker/services/nba_service.py†L1-L76】【F:python-worker/services/reminder_service.py†L1-L60】
- **Operational scripts and tests** like `test_agent_system.py` and the `tests/` suite for validating agent evolution behaviors.【F:python-worker/test_agent_system.py†L1-L20】【F:python-worker/tests/test_anomaly_detector.py†L1-L20】

### Auxiliary Tooling and Scripts
At the repository root, `github_integration.py` encapsulates REST helpers for raising GitHub issues and pull requests, while `_scan_docs.py` drives automated documentation crawls.【F:github_integration.py†L1-L78】【F:_scan_docs.py†L1-L60】 SQL definitions in `backend/create_documents.sql`, `backend/create_job_queue.sql`, and `backend/create_agent_states.sql` capture the legacy data model shared across services.【F:backend/create_documents.sql†L1-L11】【F:backend/create_job_queue.sql†L1-L13】 Additional worker scripts inside `backend/` (e.g., `crm_email_automation.py`, `user_preferences.py`) extend the automation footprint beyond the core Express runtime.【F:backend/crm_email_automation.py†L1-L22】【F:backend/user_preferences.py†L1-L22】

## Dependency Surface
- **Root orchestration** is driven by `package.json`, which wires composite npm scripts (build, test, lint) and Playwright-based end-to-end automation.【F:package.json†L1-L37】
- **Backend runtime** dependencies include Express, Drizzle ORM, OpenTelemetry, Redis, and Supabase clients declared in `backend/package.json`, alongside Jest/ESLint tooling for development.【F:backend/package.json†L1-L45】
- **Frontend stack** relies on React 18, React Router, axios, lucide-react, and Tailwind with Vitest and Testing Library for QA, as defined in `frontend/package.json`.【F:frontend/package.json†L1-L35】
- **Python worker** requirements (FastAPI, Uvicorn, Requests, python-dotenv, schedule, Pydantic) are tracked in `python-worker/requirements.txt`.【F:python-worker/requirements.txt†L1-L6】

## Deployment & Operations
Operational guidance lives in `docs/DEPLOYMENT_GUIDE.md`, detailing Supabase setup, backend build flows, and Python worker bootstrapping.【F:docs/DEPLOYMENT_GUIDE.md†L1-L93】 Container images are produced via multi-stage Dockerfiles for both the backend (Node 20 Alpine with dumb-init, health checks, and Drizzle migrations) and the Python worker (Python 3.11 slim with virtualenv promotion and health probes).【F:backend/Dockerfile†L1-L55】【F:python-worker/Dockerfile†L1-L57】 Database migrations and seeds are orchestrated with TypeScript entry points in `backend/src/database/migrate.ts` and `backend/src/database/seed.ts`, accessible through npm scripts (`db:migrate`, `db:seed`).【F:backend/src/database/migrate.ts†L1-L14】【F:backend/package.json†L7-L18】

## Notable Observations
- Legacy SQL bootstrap files coexist with Drizzle migrations; future consolidation should ensure schema drift is eliminated.
- Automation scripts appear both in the backend (Node/Python) and the standalone worker, indicating an opportunity to centralize scheduling under the refreshed automation layer.
- Documentation is distributed across `docs/` without an index, motivating the forthcoming docs re-organization captured in the refreshed structure plan.
