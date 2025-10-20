# Automation & AI Runners

## Planned Structure
Automation assets will consolidate under this workspace to clarify ownership across Python agents, Node workers, and scheduling utilities. The proposed layout is:

- `agents/` – Python and TypeScript runtimes for NBA, reminder processing, and autonomous evolution (current `python-worker/` code will land here).
- `pipelines/` – Declarative workflow definitions, queue orchestration, and event routing policies.
- `ops/` – Cron jobs, batch scripts, and operational tooling currently scattered across `backend/*.py` utilities.
- `sdk/` – Shared clients, DTOs, and authentication helpers that enable agents to talk to the backend API securely.
- `experiments/` – Sandboxes for R&D agents, benchmarking harnesses, and evaluation notebooks.
- `qa/` – Integration scenarios, load tests, and simulation harnesses covering end-to-end automation flows.

## Transition Checklist
- Migrate the FastAPI worker into `agents/python/` while preserving the REST contract documented in `backend/src/services/aiCoordinationService.ts`.
- Extract shared Supabase/Postgres access helpers into `sdk/` to eliminate duplicated SQL connectors.
- Relocate email automation, lead generation, and websocket utilities from `backend/` into `ops/` once the backend exposes stable hooks.
