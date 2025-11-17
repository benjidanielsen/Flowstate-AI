# Flowstate-AI v2030

Flowstate-AI is a next-generation, AI-powered CRM and business automation tool designed to streamline your workflow based on the **Frazer Brookes 4-part method**, expanded into a disciplined seven-stage lifecycle.

This project is in active development, refactoring from a 2-year concept into a professional, launch-ready application. The v2030 initiative embraces a clean repository, backend-first execution, and disciplined automation inspired by proven open-source systems.

## Final System Overview

Flowstate-AI acts as a self-improving sales cockpit built for network marketers and solo founders. Logging in drops the user onto a Daily Action Board that spells out today’s mission—DMO targets, prioritized follow-ups, urgent no-shows, and AI-ranked "Next Best Actions." A strict Frazer pipeline prevents stage skipping, Customer Cards aggregate every detail about a prospect, intelligent reminders run on autopilot, and analytics/gamification keep motivation high. The AI handles the heavy lifting so the human can focus on authentic conversations.

## Table of Contents

1. [Core Features](#core-features)
2. [Pipeline Management System](#pipeline-management-system)
3. [Dashboard Experience](#dashboard-experience)
4. [Customer Card System](#customer-card-system)
5. [Reminder & Automation Engine](#reminder--automation-engine)
6. [Analytics, Scoring & Gamification](#analytics-scoring--gamification)
7. [ADHD-Friendly Product Principles](#adhd-friendly-product-principles)
8. [Getting Started](#getting-started)
9. [Project Status](#project-status)
10. [Architecture Snapshot](#architecture-snapshot)
11. [Contributing](#contributing)
12. [Resources](#resources)
13. [License](#license)

## Core Features

* **AI-Powered Dashboard:** Your central command center with weighted "Next Best Action" suggestions, urgency badges, and pipeline analytics.
* **Frazer Brookes Pipeline (7 Stages):** Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → Signed-Up, with guardrails, exception statuses, and conversion reporting.
* **Customer Card System:** Complete customer profiles with interaction history, advanced filtering/search, next-step tracking, and embedded AI suggestions.
* **Intelligent Reminder Engine:** Multi-interval reminders, automated escalation rules, and inline management surfaced directly within Customer Cards.
* **Event Logging & Analytics:** Structured activity logs powering dashboards for demographics, interaction summaries, and pipeline performance.
* **AI Agent Self-Improvement:** Continuous feedback loops that help NBA agents refine strategies and escalate issues automatically.
* **Living Setup Script:** Guided onboarding that verifies dependencies, captures API keys, and provisions environment files automatically.

## Pipeline Management System

* **Strict Seven-Stage Flow:** Leads advance from Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → Signed-Up with no skipping; required fields (e.g., "Prospect’s Why") must be captured to progress.
* **Exception Handling:** Special statuses such as No-Show, Skeptical, and Lost/Closed keep analytics intact while handling edge cases.
* **Automation Hooks:** Moving a lead to key stages schedules automatic reminders (e.g., 24/48-hour follow-ups after presentations, multi-touch sequences for no-shows) and logs win/loss reasons.
* **Flexible Views:** Drag-and-drop Kanban columns plus a filterable list view provide both visual and tabular management modes.
* **Pipeline Intelligence:** Conversion rates, stage dwell times, and distribution metrics render in real time to gamify throughput.

## Dashboard Experience

* **Daily Method of Operation (DMO):** Progress bars track daily targets (new contacts, follow-ups, invitations, presentations) with instant visual feedback.
* **Prioritized Lists:** Waiting for Response, No-Shows, Hot Leads, Inactive Leads, and Unfollowed queues ensure nothing slips through the cracks.
* **Calendar Integration:** Syncs meetings (e.g., Google Calendar) and links directly to the relevant Customer Card for rapid prep.
* **NBA Command Center:** AI ranks the highest-impact actions with urgency badges and just-in-time prompts ("Send booking link to Eve").
* **Motivating Visuals:** Pipeline charts, performance trends, leaderboards, and habit trackers reward consistent action.

## Customer Card System

* **360° Prospect Snapshot:** Contact info, preferred channel, pipeline status, tags, AI scores, and the "Next Step" tile stay visible at all times.
* **Rich Interaction Timeline:** Calls, messages, meetings, notes, and tasks log chronologically with timestamps and channels.
* **Advanced Filtering/Search:** Indexed fields support deep filtering (e.g., interest level, location, tags) for targeted outreach.
* **AI Insights:** Relationship Level (1–5), Interest Level (1–5), Priority Grade (A/B/C), and AI conversion probability guide focus.
* **Guided Actions:** Dedicated UI for adding interactions, scheduling next steps, and responding to AI recommendations without context switching.

## Reminder & Automation Engine

* **Multi-Interval Cadences:** Configure single, recurring, or escalating reminders per lead or playbook.
* **Status-Aware Escalation:** Automated sequences trigger for no-shows (e.g., 2h/1d/3d) and adjust cadence by pipeline stage.
* **Inline Management:** Create, update, snooze, or cancel reminders directly from the Customer Card while seeing history.
* **Python Worker Backbone:** Celery beat + workers process due reminders, send notifications, and update reminder states.

## Analytics, Scoring & Gamification

* **Event Logging Fabric:** Structured JSON events capture interactions, pipeline transitions, reminders, and AI outcomes for downstream analytics.
* **Insight Dashboards:** Demographics, interaction summaries (totals, averages per customer), conversion funnels, and win/loss trends surface in the UI.
* **Lead Scoring:** Relationship, interest, priority, and AI probability combine to populate Hot Lead queues and NBA weighting.
* **Gamified Momentum:** Stage counts, conversion bars, badges, streaks, and daily/weekly challenges keep users motivated.

## ADHD-Friendly Product Principles

* **One-Thing-at-a-Time UI:** Focused modals and collapsible sections expose only what matters now.
* **Immediate Feedback:** Progress bars, celebratory animations, and alerts confirm every action.
* **Visual Clarity:** Color coding, icons, and motion convey urgency and success with minimal cognitive load.
* **Safe Exploration:** Undo options and confirmations make the system "dummy-proof." Users can’t accidentally break the pipeline.
* **Always-On Guidance:** Inline tooltips and an AI help chat teach CRM concepts in context.

## Getting Started

### Prerequisites

* Python 3.11+
* Node.js 18+
* Docker & Docker Compose
* An [OpenAI API Key](https://platform.openai.com/api-keys)

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/benjidanielsen/flowstate-ai-v2030.git
    cd flowstate-ai-v2030
    ```

2.  **Run the interactive setup script:**
    This script will help you create your `.env` file and set up your API keys.
    ```bash
    python3 scripts/setup.py
    ```

3.  **Launch (Docker Recommended):**
    The easiest way to get started is with Docker.
    ```bash
    docker compose up --build
    ```

4. **Smoke Test the Backend:**
    ```bash
    curl http://localhost:8000/health
    ```

### Local Development (Manual)

*Backend*

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

*Frontend*

```bash
cd frontend
npm install
npm run dev
```

## Project Status

* **Phase:** Sprint 0 Preparation
* **Backend Priority:** FastAPI service initialization, PostgreSQL schema, and health check endpoint.
* **Pipeline Blueprint:** Seven-stage Frazer pipeline enumerated and analytics requirements captured in the Blueprint.
* **Frontend Priority:** Post-backend scaffolding (Next.js dashboard shell).
* **Automation Priority:** Celery worker skeleton with Redis broker and LangChain proof-of-concept for NBA suggestions and reminder processing.

## Architecture Snapshot

| Layer | Stack | Notes |
| --- | --- | --- |
| Backend | FastAPI · SQLAlchemy · Pydantic · Celery | Backend-first; API is the product surface area. |
| Database | PostgreSQL · Alembic | Structured schemas for pipeline, customer cards, activities. |
| AI | OpenAI API · LangChain · Redis Cache | Automations and NBA suggestions with cached prompts. |
| Frontend | Next.js · TypeScript · Tailwind CSS | Dashboard-first UX; mirrors backend contract. |
| Tooling | Docker Compose · Ruff · Black · ESLint · Playwright | Enforced via CI and pre-commit hooks. |

## Contributing

1. Fork the repository.
2. Create a feature branch (e.g., `feat/pipeline-stage-api`).
3. Commit your changes with clear messages.
4. Open a pull request referencing the relevant section of `PROJECT_BLUEPRINT.MD`.
5. Ensure `docker compose up --build` and `pytest` succeed locally prior to review.

## Resources

* [Project Blueprint](docs/PROJECT_BLUEPRINT.MD)
* [Developer Guide](docs/DEVELOPER_GUIDE.md)
* [Legacy Repository (Archived)](https://github.com/benjidanielsen/Flowstate-AI/)

## License

This project will adopt an open-source license in Sprint 1. Until then, all rights are reserved by the maintainers.
