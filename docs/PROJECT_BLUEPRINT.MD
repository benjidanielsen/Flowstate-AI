# Flowstate-AI v2030: The Turnaround Blueprint

## 1. Executive Summary & Status

* **Project:** Flowstate-AI v2030
* **Vision:** An AI-powered CRM built on the Frazer Brookes 4-part methodology.
* **Current Status:** Phase 0 (Analysis-Paralysis). The project is stalled due to a lack of clear architectural decisions and a defined execution path. Technical discovery overran execution, leaving fragmented subsystems and competing tooling strategies.
* **Turnaround Goal:** To exit Phase 0 by finalizing this blueprint, making a definitive repo decision, and beginning "Sprint 0" within 24 hours.
* **Critical Success Metrics:** (1) New repo scaffolding merged, (2) backend health-check endpoint deployed locally via Docker, (3) interactive setup script provisioning `.env` secrets without manual editing.

## 1.1 Final System Overview

Flowstate-AI v2030 is an ADHD-friendly, AI-powered CRM that keeps solo founders and network marketers focused on the exact next action required to advance every prospect. Users log in and immediately land on a Daily Action Board that surfaces their DMO goals, prioritized follow-ups, and NBA recommendations. A strict seven-stage Frazer pipeline governs progression from first contact through signed team member, while Customer Cards consolidate every detail—contact context, interaction history, AI scores, and next steps—into one "don’t-think-about-it" workspace. Reminder automation, analytics, and AI self-improvement loops operate behind the scenes so that the human only performs the high-impact conversations.

The end result is a self-improving sales operating system: the pipeline enforces best practices, the dashboard gamifies progress, the reminder engine keeps commitments on track, and the AI continuously learns from outcomes to refine recommendations.

## 2. Breakpoint Decision: New Repo vs. In-Place Refactor

The legacy repository contains multiple experimental subsystems, abandoned automation scripts, and numerous untracked dependencies. Its Git history shows repeated pivots without consolidation, which makes future maintenance risky.

### Option A: In-Place Refactor (Build in the Old Repo)
* **Pros:**
  * Maintains the existing issue history and any partially implemented ideas for future reference.
  * Requires no change to existing CI/CD integrations or permissions.
* **Cons:**
  * Tangled dependency tree and conflicting tooling versions add significant stabilization time.
  * Difficult to enforce a backend-first architecture without first deleting or archiving large parts of the codebase.
  * High cognitive load for new contributors navigating obsolete scripts and directories.
* **Analysis:** Keeping development in the current repository prioritizes continuity over clarity. Every sprint would begin with defensive cleanup to avoid breaking legacy scripts. This approach is incompatible with the goal of shipping a stable backend quickly.

### Option B: Clean Repo (Start Fresh, Archive Old)
* **Pros:**
  * Enables a curated, backend-first structure aligned to the blueprint from day one.
  * Eliminates dependency drift by reintroducing packages deliberately.
  * Creates a psychological "reset" that signals the end of experimentation and the start of execution.
* **Cons:**
  * Requires migrating any still-valuable assets (documentation, schemas) manually.
  * Demands coordination to archive or snapshot the old repository for posterity.
* **Analysis:** Starting fresh allows us to import only the ideas that support the v2030 direction. Valuable artifacts from the old repo can be selectively ported into `/docs/archive` as needed without dragging along technical debt. This keeps velocity high and forces disciplined decision-making. It also lets us implement automated quality gates (lint, type-check, unit test) from commit one without suppressing legacy failures.

### **Final Recommendation & Justification:**
Recommendation: **Clean Repo.** The 2-year history, while rich in ideas, is now mostly technical debt. A clean slate is the fastest, most stable way to enforce a backend-first build, unify tooling, and permanently break the "going in circles" loop. The legacy repository will be archived and referenced only for inspiration.

## 3. Competitive Analysis & "Steal Like an Artist" Strategy

* **Inspiration Project 1:** `Odoo CRM`
  * **What they do well:** Mature, modular customer management with robust contact, pipeline, and activity models.
  * **"Wheel" to Adapt:** Reuse their contact/pipeline data model concepts (e.g., separate tables for partners, activities, and stages) to bootstrap our Customer Card schema and pipeline transitions. Adopt their approach to computed fields for sales velocity and integrate similar computed metrics into our dashboard service.

* **Inspiration Project 2:** `LangChain`
  * **What they do well:** Composable agent and tool abstractions that streamline AI decision-making and integrations with LLMs.
  * **"Wheel" to Adapt:** Use LangChain's agent architecture for our AI Assistant and NBA logic—particularly tools for note summarization, intent extraction, and scheduling suggestions. We will mirror their memory interfaces for conversation context and adapt their `AgentExecutor` pattern for multi-step NBA workflows.

* **Inspiration Project 3:** `Supabase CLI`
  * **What they do well:** A friendly, scriptable onboarding experience that interactively gathers secrets and scaffolds environment files.
  * **"Wheel" to Adapt:** Model our "living setup script" on their CLI flow—validate dependencies, prompt for API keys, and generate `.env` and Docker overrides automatically.

* **Inspiration Project 4:** `Appsmith`
  * **What they do well:** Open-source, widget-driven dashboards with granular RBAC and audit logging.
  * **"Wheel" to Adapt:** Adopt their pattern of centralizing UI state in a store (e.g., Zustand) and providing role-based visibility controls for dashboard widgets. This accelerates the dashboard MVP while ensuring extensibility.

## 4. Recommended v2030 Tech Stack

* **Backend:** Python 3.11 + FastAPI, SQLAlchemy, Pydantic, Celery for async automations.
* **Frontend:** Next.js (React 18, TypeScript, Tailwind CSS) for a modern dashboard experience.
* **Database:** PostgreSQL + SQL migrations (Alembic) for relational consistency.
* **AI Integration:** OpenAI API orchestrated through LangChain, plus Redis for caching AI responses and Celery tasks.
* **Observability:** OpenTelemetry instrumentation with exporters to Grafana Tempo/Loki via Docker Compose.
* **Deployment:** Docker + Docker Compose for local dev; Terraform modules for future cloud infra; GitHub Actions CI.

**Recommendation:** This stack balances developer velocity with long-term maintainability. FastAPI and SQLAlchemy provide typed, testable backend services that integrate naturally with LangChain. Next.js delivers a component-driven UI with SSR/ISR options. PostgreSQL anchors the CRM data model, while Docker Compose ensures reproducible environments across contributors.

## 5. Recommended v2030 Repo Structure

**Proposed Structure (Assuming "Clean Repo"):**
```
flowstate-ai-v2030/
├── backend/
│   ├── app/
│   │   ├── api/            # API endpoints (routers)
│   │   ├── core/           # Config, settings, AI logic
│   │   ├── models/         # Database models (SQLAlchemy)
│   │   ├── schemas/        # Pydantic response/request models
│   │   └── services/       # Business logic and orchestration
│   ├── alembic/            # Database migrations
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/
│   ├── components/
│   ├── pages/
│   ├── public/
│   └── package.json
├── scripts/
│   └── setup.py            # The "living setup script"
├── docs/
│   ├── PROJECT_BLUEPRINT.MD
│   └── DEVELOPER_GUIDE.MD
├── .env.example
├── .gitignore
└── README.md
```

*(**Note:** The old repo `Flowstate-AI` will be archived.)*

## 6. Core Feature Deep-Dive

### 6.1. The Dashboard
* **What it is:** The user's main control center.
* **How it works:** Presents a Daily Action Board that highlights DMO goals (e.g., 20 new contacts, 30 follow-ups, 5 invitations, 3 presentations) with live progress bars. Specialized lists—Waiting for Response, No-Shows, Hot Leads, Inactive Leads, Unfollowed Leads—surface the right contacts at the right moment. Calendar sync injects upcoming meetings with quick links to Customer Cards, while the NBA widget ranks AI-prioritized tasks with urgency indicators. Pipeline charts, performance trends, leaderboards, and habit trackers create gamified feedback so the user always knows if they are winning the day.
* **Status:** Planned
* **Dependencies:** Backend API (all other modules).

### 6.2. The Pipeline System (Frazer Brookes Method)
* **What it is:** The core CRM workflow, managing a prospect's journey.
* **Underlying Principle:** Based *specifically* on **Frazer Brookes's 4-part daily method**, expanded into seven operational stages for execution clarity.
* **How it works:** A Kanban board that enforces the seven-stage progression required by the business:
    1. `Lead` (New prospect captured)
    2. `Relationship` (Active rapport building)
    3. `Invited` (Prospect accepted an invite)
    4. `Qualified` (Prospect validated as ideal fit)
    5. `Presentation Sent` (Materials delivered)
    6. `Follow-Up` (Ongoing engagement to close)
    7. `Signed-Up` (Customer converted)
* **Automation & Guardrails:**
    * Mandatory data capture (e.g., "Prospect's Why") blocks premature stage changes so no step is skipped.
    * Automatic follow-up tasks fire when a lead enters key stages (e.g., 24–48h reminders after `Presentation Sent`, multi-touch sequences for `No-Show`).
    * Inactivity monitors flag leads untouched for 7+ days and push them into attention queues.
    * Special exception statuses (`No-Show`, `Skeptical`, `Lost/Closed`) let users handle detours without breaking analytics.
* **Analytics:**
    * Kanban and list views share pipeline counts, conversion rates, and stage dwell times to gamify throughput.
    * Win/loss logging with AI auto-categorization surfaces patterns (price, timing, disinterest) for continuous improvement.
* **Status:** Planned
* **Dependencies:** Customer Card module, Reminder module, Audit logging service, Analytics warehouse.

### 6.3. Customer Card
* **What it is:** The central record for a single prospect or customer.
* **How it works:**
    * Maintains complete profiles (contact data, preferred channel, pipeline status, tags, demographics) with an always-visible "Next Step" block.
    * Supports advanced filtering, searching, and sorting aligned with Odoo-inspired schemas so power users can slice the database instantly.
    * Logs all interactions (calls, messages, meetings, notes) with timestamps, authorship, and channel metadata in a chronological timeline.
    * Provides dedicated UI widgets to add interactions and schedule next actions, including due dates and owners, without leaving the card.
    * Surfaces AI-powered smart recommendations for next steps inline with the NBA engine, and displays AI-computed metrics (Relationship Level 1–5, Interest Level 1–5, Priority A/B/C, AI conversion probability) to aid decision-making.
* **Status:** Planned
* **Dependencies:** Database, Pipeline module, Notes module, Analytics service, AI Assistant.

### 6.4. Intelligent Reminder System
* **What it is:** The automation layer that keeps follow-ups and commitments on schedule.
* **How it works:**
    * Enables multi-interval reminders (single, recurring, escalated sequences) configured per customer or playbook.
    * Executes automated escalation rules that adjust cadence based on pipeline stage, status (e.g., `No-Show`), and inactivity thresholds.
    * Exposes CRUD management directly within the Customer Card so users can create, update, snooze, or cancel reminders inline while seeing history.
    * A Python worker (Celery beat + worker) processes due reminders, handles progressive sequences (2h/1d/3d for no-shows), and dispatches notifications/webhooks.
* **Status:** Planned
* **Dependencies:** Celery workers, Redis broker, Customer Card, Pipeline module, Notification service.

### 6.5. AI Assistant & NBA
* **What it is:** A proactive AI that suggests actions and automates tasks.
* **How it works:** Uses "wheels" from our Competitive Analysis (e.g., LangChain agents).
    * Scans notes and conversations for intent (e.g., "call next week") to auto-create reminders.
    * Generates weighted "Next Best Action" (NBA) recommendations with urgency indicators.
    * Operates in global mode (dashboard overview) and customer-specific mode (embedded inside Customer Card).
* **Status:** Planned
* **Dependencies:** OpenAI API Key, Notes module, Reminder module, Redis cache, Celery workers, Analytics signals.

### 6.6. Event Logging & Analytics
* **What it is:** The observability backbone for customer interactions and system behavior.
* **How it works:**
    * Persists structured JSON events for all customer interactions, reminders, pipeline transitions, AI actions, and gamification milestones.
    * Powers advanced reporting dashboards with demographics (country, language, source), interaction summaries (counts, totals, averages per customer), and conversion funnels.
    * Feeds performance tracking metrics that inform NBA prioritization, pipeline health visualizations, and self-improvement loops.
* **Status:** Planned
* **Dependencies:** PostgreSQL (events table), Loki log sink, Analytics warehouse, Dashboard widgets.

### 6.7. AI Agent Self-Improvement
* **What it is:** Continuous improvement loops for the AI Assistant and automation agents.
* **How it works:**
    * Agents log self-evaluations against predefined KPIs after executing tasks and compare outcomes to historical baselines.
    * Feedback loops adjust model parameters, prompt templates, scoring weights, and escalation rules based on outcomes.
    * Significant degradations automatically raise GitHub issues for human or AI investigation, assigning severity based on impact.
* **Status:** Planned
* **Dependencies:** AI Assistant, Event Logging service, GitHub integration, Analytics warehouse.

### 6.8. Scoring, Gamification & Motivation
* **What it is:** Mechanics that keep users engaged and oriented.
* **How it works:**
    * Lead scoring synthesizes Relationship Level, Interest Level, Priority tier, and AI conversion probability to populate Hot Lead queues.
    * Pipeline gamification features stage counts, conversion progress bars, badges ("First Lead Converted", "5 Meetings Booked"), and streak trackers for DMO completion.
    * Daily and weekly challenges visualize progress with celebratory micro-interactions and positive reinforcement when goals are met.
* **Dependencies:** Event Logging, Dashboard widgets, NBA Engine.

### 6.9. ADHD-Friendly, "Dummy-Proof" Experience
* **What it is:** Design philosophy ensuring clarity and safety.
* **How it works:**
    * One-thing-at-a-time UI surfaces only the most relevant action, hiding advanced options behind focused modals.
    * Immediate feedback (progress bars, confetti, alerts) confirms every action.
    * Color-coding, icons, and animations communicate urgency and success without cognitive overload.
    * Undo/safety nets protect against accidental destructive actions; confirmations and reversible operations are standard.
    * Inline tooltips and an always-available AI help chat provide contextual guidance and onboarding.
* **Dependencies:** Frontend components, NBA Engine, AI Assistant.

### 6.10. End-to-End Daily Workflow
* **Scenario:** User logs in, reviews three AI-curated tasks, and completes them via direct Customer Card actions.
* **System Support:**
    * Pipeline transitions auto-create follow-ups and respect guardrails.
    * NBA panel continuously updates with highest-impact actions.
    * Reminder engine schedules future nudges while logging outcomes.
    * Dashboard analytics reflect progress against DMO goals and conversion trends before sign-off.

## 7. Function & Automation Matrix ("What does What, When")

| Function | Trigger (When) | Action (What) | Purpose (Why) |
| :--- | :--- | :--- | :--- |
| New Prospect | User adds a new prospect. | Prospect is placed in "Lead" (Stage 1) pipeline. | To start the journey. |
| Follow-up Reminder | Card moved to "Follow-Up" (Stage 6). | Create a reminder sequence (3, 7, 14 days) with escalating urgency. | To ensure the user "Keeps Talking" (FB method). |
| Multi-Interval Reminder | User configures a recurring reminder. | Persist cadence, enqueue Celery schedule, and confirm via UI toast. | Provide flexible reminder scheduling. |
| AI Note Analysis | User saves a new note. | AI scans note for dates/intent (e.g., "call next Tuesday"). | Auto-create a reminder for "call [Prospect] next Tuesday". |
| AI NBA | User logs into Dashboard. | AI scans all prospects for inactivity, priority score, stage dwell time, and overdue reminders. | Display weighted "Next Best Action" list with urgency badges. |
| Easy Setup Script | User runs `setup.py` for the first time. | Script checks for `.env`. If missing, prompts user: "Paste your OpenAI API key:" | To make user setup seamless and non-technical. |
| Data Snapshot | Daily at 02:00 UTC (Celery beat). | Export anonymized pipeline metrics to S3-compatible storage. | Preserve analytics for trend reporting without risking data loss. |
| Event Logging | Interaction recorded or pipeline stage changes. | Write JSON event to PostgreSQL + stream to Loki. | Maintain compliance-ready change history and analytics. |
| AI Self-Evaluation | NBA recommendation executed. | Agent records outcome score, adjusts weightings, and opens GitHub issue if below threshold. | Sustain continuous improvement without manual oversight. |

## 8. The "Get Unstuck" Action Plan (Sprint 0)

* **Step 1: User Approval:** User (benjidanielsen) must approve this Blueprint (Sections 2, 3, 4).
* **Step 2: Repo Execution:**
    * **If Clean Repo:** I (Architect) will provide commands to:
        1. Create the new `flowstate-ai-v2030` repo.
           ```bash
           gh repo create benjidanielsen/flowstate-ai-v2030 --private --description "Flowstate-AI v2030 clean reboot"
           git remote set-url origin git@github.com:benjidanielsen/flowstate-ai-v2030.git
           ```
        2. Archive the old `Flowstate-AI` repo (make it read-only).
           ```bash
           gh repo edit benjidanielsen/Flowstate-AI --archived=true --default-branch=main
           ```
    * **If In-Place:** I (Architect) will provide commands to:
        1. Create a new `v2030-refactor` branch.
        2. Move all old files into a `/backup/` folder.
* **Step 3: Generate Foundation:** I (Architect) will provide the *full* code for:
    1. The complete repo folder structure (from Section 5).
    2. All config files (`.env.example`, `.gitignore`, `Dockerfile`, `requirements.txt`).
    3. The `README.md` and `DEVELOPER_GUIDE.md` drafts.
    4. GitHub Actions workflows for lint (`ruff` + `eslint`) and tests (`pytest` + `playwright test`).
* **Step 4: Backend Sprint 0 (Day 1 Build):**
    * I (Architect) will provide the code to initialize the backend (e.g., FastAPI) and database connection.
    * We will build the *first* API endpoint (e.g., `/health`) and *confirm it works* via Docker.
        ```bash
        cd backend
        docker compose up --build api db redis
        curl http://localhost:8000/health
        ```
    * After validation, publish the container image to the container registry configured in Sprint 1 (placeholder: `ghcr.io/benjidanielsen/flowstate-api`).

**Risk Radar & Mitigations:**

1. **Scope Creep:** Any feature outside Sections 5–7 requires a Blueprint update and approval before work begins.
2. **Secret Management:** Until Vault integration, secrets are stored via the setup script and `.env` only. Enforce `pre-commit` hooks to prevent accidental commits.
3. **AI Cost Overruns:** Implement rate limiting and caching on LangChain tools; review API usage weekly during Sprint 0.

**This plan moves us from "talking" to "building" immediately.**
