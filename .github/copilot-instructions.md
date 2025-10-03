# Flowstate-AI Copilot Instructions

## Architecture snapshot
- Monorepo with four active services: `frontend/` (React + Vite + Tailwind), `backend/` (Express + TypeScript + SQLite), `python-worker/` (FastAPI reminders/NBA engine), and `godmode-dashboard/` (Flask + Socket.IO monitor).
- Root `package.json` orchestrates workspace scripts (build/lint/test/dev) and Playwright E2E runs; keep changes within this root - the workspace path already nests `Flowstate-AI/Flowstate-AI`, so avoid creating another clone inside.
- SQLite dev data lives under `./data/flowstate.db`; backend `DatabaseManager` and Python worker services both bind to the same file via `DATABASE_URL`. Docker Compose swaps to Postgres when the `production` profile is used.

## Developer workflows
- Install everything with `npm run setup` (installs root/front/back plus `python-worker` requirements) and copy `backend/.env.example` before launching services.
- Daily loop: `npm run dev` starts backend (`ts-node-dev`) and frontend (`vite`); run the worker separately with `cd python-worker && python -m uvicorn src.main:app --reload` when reminder/NBA APIs are required.
- Database: run `npm run db:migrate` then `npm run db:seed` from the repo root; both commands execute backend TypeScript scripts and write to `data/flowstate.db`.
- Quality gates: `npm run lint` / `npm run lint:fix` cascade into both Node workspaces, `npm run test:frontend` (Vitest), `npm run test:backend` (Jest with `--detectOpenHandles`), and `npm run test:e2e` (Playwright spins dev servers on ports 3000/3001 - make sure they are free). Install browsers once with `npx playwright install chromium`.
- Python components do not yet ship automated tests; follow the FastAPI pattern in `python-worker/src` and add `pytest` suites alongside new logic.

## Backend conventions
- Express routing lives under `backend/src/routes`, each delegating to controller classes in `backend/src/controllers/` which wrap services under `backend/src/services/`.
- Services talk directly to SQLite via `DatabaseManager` (see `backend/src/database/`) and must log significant customer events using `EventLogService` so analytics and dashboards stay accurate.
- Frazer Method stages are validated by `PipelineValidationService`; any new status or progression rule belongs there and should also update `CustomerService.moveCustomerToNextStage` plus reminder logic.
- Reminder automation in the backend persists records via `ReminderService`; time-based follow-ups triggered by events funnel through `AutomationService`.
- Cross-service calls to the Python worker should reuse the existing HTTP helpers and respect the `PYTHON_WORKER_URL` environment variable rather than inlining new clients.

## Frontend conventions
- Structure: Routed pages in `frontend/src/pages/`, shared UI in `components/`, hooks/contexts encapsulate state (`contexts/ToastContext.tsx` for notifications).
- API access is centralized in `frontend/src/services/api.ts`; extend these helpers (and the accompanying TypeScript types in `frontend/src/types/`) instead of ad-hoc `fetch` calls.
- Pipeline enums differ slightly from backend naming; update both sides together so stage labels, reminder automation, and stats remain aligned.
- Styling leans on Tailwind utility classes plus `index.css`; prefer composing primitives over introducing new global styles.

## Python worker & dashboards
- `python-worker/src/main.py` exposes async FastAPI endpoints; reminder orchestration lives in `services/reminder_service.py`, and NBA logic in `services/nba_service.py`. Both write to the shared SQLite file - keep operations idempotent and guard against long-running sync work.
- Reminder schedules depend on Frazer stages; modify the dictionaries in `ReminderService` when stages change so automation keeps pace with backend rules.
- The Godmode dashboard (`godmode-dashboard/app_enhanced.py`) streams agent telemetry, logs to `godmode-dashboard/logs/`, and can open GitHub issues through `github_integration.py`. Preserve the Socket.IO events and logging structure when extending it.

## CI & operations
- GitHub Actions live in `.github/workflows/`; align new scripts with root npm tasks so CI picks them up automatically.
- `docker-compose.yml` shares a `./data` volume between backend and worker containers; production profile enables Postgres. Keep database-agnostic SQL where possible so migrations run on both SQLite and Postgres.
- Document cross-service contract changes (API shapes, DB schema, reminder cadence) in the relevant README under `docs/` and update this guide when behavior shifts.

