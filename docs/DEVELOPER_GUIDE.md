# Developer Guide

Welcome to the Flowstate-AI v2030 project. This document outlines the project architecture, standards, and how to contribute.

## 1. Guiding Principles

1. **Backend-First:** The backend API is the source of truth. It must be fully functional and tested before any frontend UI is built for it.
2. **Blueprint-Driven:** All new features or changes *must* be proposed and agreed upon in the `PROJECT_BLUEPRINT.MD` *before* implementation. This prevents scope creep and keeps us from "going in circles."
3. **Steal, Don't Reinvent:** Before building a complex component (e.g., a data model, an AI agent), check the "Competitive Analysis" in the Blueprint. We adapt proven solutions.

## 2. Architecture Overview

* **Backend:** FastAPI (Python 3.11), SQLAlchemy, Pydantic, Celery, Redis, OpenTelemetry
* **Frontend:** Next.js (React 18, TypeScript, Tailwind CSS, Zustand)
* **Database:** PostgreSQL (managed via Alembic migrations)
* **Repo Strategy:** Clean repository beginning Sprint 0. The legacy v1 project is archived at `https://github.com/benjidanielsen/Flowstate-AI/`.
* **Tooling:** Docker Compose, pre-commit, Ruff, Black, Pytest, ESLint, Playwright, GitHub Actions.

## 3. Domain Modules

* **Pipeline:** Seven canonical stages (Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → Signed-Up) stored as enum constants. Stage transitions emit analytics events, enforce required field validations (e.g., Prospect Why), and trigger reminder adjustments. Special statuses (`NO_SHOW`, `SKEPTICAL`, `LOST_CLOSED`) live alongside the main enum for reporting.
* **Customer Cards:** CRUD endpoints expose full profile data, interaction logs, tags, and next-step metadata. Support indexed search/filter queries, computed AI scores, and embed NBA responses inline with actionable buttons (log call, send reminder, schedule meeting).
* **Reminder Engine:** Celery beat schedules manage multi-interval reminders, escalation policies, no-show sequences (2h/1d/3d), and manual overrides originating from Customer Cards or pipeline events.
* **NBA Engine:** LangChain agents compute weighted priorities using event stream metrics, lead scores, and reminder state; exposes both global and customer-specific recommendation endpoints with urgency ranks.
* **Dashboard Service:** Aggregates DMO progress, prioritized lists (Waiting for Response, No-Shows, Hot Leads, Inactive, Unfollowed), calendar sync data, and renders gamification metrics (badges, streaks, conversion charts).
* **Event Logging:** Structured JSON events persist to PostgreSQL and stream to Loki. Downstream analytics queries feed dashboards, win/loss reports, and AI self-improvement KPIs.
* **AI Feedback Loop:** Post-action webhooks record agent performance, tune weights, and can open GitHub issues automatically when outcomes fall below thresholds.

## 4. How to Contribute

1. Create a new feature branch (e.g., `feat/ai-assistant-suggestions`).
2. Implement code following the repo structure defined in `PROJECT_BLUEPRINT.MD`.
3. Write unit tests for any new backend logic.
4. Run formatting/linting (e.g., `ruff`, `black`, `pytest`) before committing.
5. Submit a Pull Request for review, referencing the relevant Blueprint section.

## 5. Branching & Release Strategy

* **Default Branch:** `main` (protected; requires PR review and green CI).
* **Feature Branches:** `feat/<scope>`, `fix/<scope>`, `chore/<scope>`.
* **Release Tags:** Semantic versioning beginning with `v0.1.0` at Beta launch.
* **Hotfixes:** Branch from the release tag, prefix with `hotfix/`, merge back into `main` and re-tag.

## 6. Backend Standards

* **API Design:** RESTful FastAPI routers grouped by domain (`/customers`, `/pipeline`, `/dashboard`, `/automation`).
* **Schemas:** Use Pydantic models in `app/schemas` for request/response validation. Include computed field outputs (AI scores, progress metrics) explicitly.
* **Services:** Encapsulate business logic in `app/services`. Routers should remain thin and orchestrate service + event logging calls.
* **Data Access:** Prefer SQLAlchemy ORM models. For complex queries, use repository helpers within `app/services`.
* **Asynchronous Tasks:** Register Celery tasks under `app/services/automation.py` and ensure idempotency. Reminder escalations, NBA recomputations, and DMO analytics refreshes must be retry-safe.
* **Testing:** Add tests in `backend/tests` mirroring module structure; use `pytest` fixtures for database and Redis. Provide fixtures covering reminder schedules, stage guardrails, and event logging.

## 7. Frontend Standards

* **State Management:** Use Zustand stores colocated with features (inspiration from Appsmith RBAC patterns). Stores should expose selectors for prioritized lists (e.g., `useHotLeads`, `useNoShows`).
* **Styling:** Tailwind CSS utility classes plus component-level variants; avoid inline styles.
* **API Layer:** Create typed clients in `frontend/lib/api.ts` that map to backend schemas, including pagination/filter parameters for list views.
* **Testing:** Implement unit tests with Vitest and component tests with Playwright. Ensure dashboards render analytics widgets, reminder controls, and pipeline guardrails accurately (e.g., stage move blocked without Prospect Why).

## 8. Tooling & Automation

* **Pre-commit:** Install hooks via `pre-commit install` to enforce formatting, secret scanning (e.g., `detect-secrets`), and forbid accidental deletion of critical pipeline constants.
* **CI/CD:** GitHub Actions workflows run lint, type-check, tests, and Docker build on every PR.
* **Observability:** Instrument backend endpoints with OpenTelemetry and export traces/logs in local Docker Compose stack (Grafana Tempo/Loki). Ensure event logging produces both metrics and structured logs for NBA feedback loops.

## 9. Communication Protocols

* **Daily Update:** Post progress and blockers in `PROGRESS_LOG.md` or the designated communication channel.
* **Decision Log:** Significant architecture changes require an ADR entry under `docs/decisions/`.
* **Meeting Cadence:** Twice-weekly syncs focused on Sprint goals; async updates preferred otherwise.
