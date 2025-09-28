
# FlowState OS — Implementation Kickoff & Command Pack (Tool-Agnostic, Versionless)

**Purpose:** Give this file to an advanced AI (e.g., Gemini) *in the same chat as your blueprint*. It contains a single **orchestrator prompt** and concrete **build commands** so the AI can move from blueprint ➝ real, running system. Tool-agnostic by default; when implementation requires a choice, the AI must propose 2–3 viable stacks with trade-offs and pick one on your approval.

---

## 0) How to use this
1) Paste the **Implementation Orchestrator** block into the AI.  
2) When it returns options, reply with one of the **Build Commands** below (No-Code Track or Code Track).  
3) Keep the conversation **in one thread** so the AI can iteratively improve and deliver assets.  
4) Bring the **Testpack** and **Checklist** we already created; ask the AI to use them in simulation/UAT.

> Files you can upload alongside this document:
> - `NWM_CRM_Testpack_v1.zip` (synthetic data + schemas + simulation templates)  
> - `NWM_CRM_ZeroBased_Checklist.md` (delivery checklist)

---

## 1) Implementation Orchestrator (copy-paste this first)

**IMPLEMENTATION ORCHESTRATOR — VERSIONLESS**  
**Role & Mode:** Act as Principal System Architect + Delivery Lead. Use the latest FlowState OS blueprint in this chat as the **Baseline**. Tool-agnostic by default. English output. No chain-of-thought; deliver artifacts.

**Goal:** Turn the Baseline blueprint into a **running MVP** with minimal Time-to-IPA and ≤ 3 clicks to “Next Action”.

**Process (single response):**
1) **Stack Options:** Propose 2–3 viable implementation paths (e.g., a no-code stack; a code stack). Give trade-offs (result, complexity, cost, limits, time-to-ship). Recommend one for MVP.  
2) **Scope Split:** Outline the MVP scope (what ships now) vs. Phase-Next (what waits).  
3) **Execution Plan:** Break into workstreams (Data, Backend/API or Data Automations, Frontend/UI, Integrations, Testing/UAT, Deployment). Provide a sprintable plan with concrete deliverables and acceptance criteria.  
4) **Artifacts to Produce Now:** List exact files you will generate **in this chat** (schemas, OpenAPI, UI wireframes, automations specs, scripts).  
5) **Risk/Assumptions:** State assumptions and top 5 risks with mitigations.  
6) **Ask for Confirmation:** Stop after the plan and ask which path to execute. If I answer “Proceed”, generate all artifacts you promised, ready to run/import.

**Constraints & Quality Gates:**  
- Keep it **tool-agnostic** unless I approve a stack; then produce stack-specific assets.  
- Honor the blueprint’s **NBA, state machine, automation rules, NFR/SLO**.  
- Use the uploaded **Testpack** to seed data and run simulation; fill the **Effect Matrix** and produce BEFORE/AFTER numbers for Time-to-IPA.  
- Provide **copy-pasteable** assets (JSON/YAML/CSV/SQL/OpenAPI, UI blueprints, automation recipes).  
- End with a **Go/No-Go** and a **Next Iteration Plan** if not 🟢.

---

## 2) Build Commands — No-Code Track (pick one and paste after the Orchestrator approves)

### A) “No-Code MVP — Relational Base + Automations”
**Command:**  
“**Execute No-Code MVP**: Create a relational data model (Prospects, Interactions, Tasks), interface screens (Dashboard with NBA top-5, Prospect card, Tasks board), and event automations for No-Show (2–6h + next day 12/16), Video (~24h), Re-engagement (1w→2w→1m→2m), and IPA Coach (08:00 + 4–6 micro-pings). Deliver: (1) table schemas with field types, validation rules; (2) interface wireframes; (3) automation recipes (trigger→filters→actions) in a copy-paste format; (4) import mapping from `testdata_*.csv`; (5) step-by-step import guide; (6) UAT plan with pass/fail criteria. Use the Testpack and fill Effect Matrix + NBA Queue Template with measured results.”

### B) “Calendar & Messaging Integration — Spec First”
**Command:**  
“**Design Calendar & Messaging Integration**: Provide a platform-agnostic spec to parse meeting titles (‘Intro – [Name]’) → link to Prospect → trigger follow-ups. Include: event parsing rules, duplicate handling, race conditions, backfill strategy, and rate-limit-safe polling schedule. Add message template structures (variables, short/long) for warm/cold invites, T-24/T-2, post-presentation, objections, closing, retention. Keep tool-agnostic; produce copy-pasteable pseudo-workflows.”

---

## 3) Build Commands — Code Track (pick one and paste after the Orchestrator approves)

### C) “Repo & API Scaffold — Portable Spec First”
**Command:**  
“**Generate a portable implementation pack**:  
1) **Repo tree** and README.  
2) **OpenAPI 3.0 YAML** for endpoints: `/health`, `/prospects`, `/interactions`, `/tasks`, `/nba/next`, with request/response schemas and error model.  
3) **DB schema**: SQL for `prospects`, `interactions`, `tasks`, `audit_log`, enums, FKs, indexes.  
4) **Migrations** (idempotent).  
5) **Seed scripts** to import `testdata_*.csv`.  
6) **NBA algorithm** (deterministic reference implementation, language-agnostic pseudocode + one runnable variant in a mainstream language).  
7) **Docker compose** for DB + API + Adminer/pgAdmin (local dev).  
8) **UAT test plan** using the Testpack + Effect Matrix updates.  
Deliver all as **copy-paste blocks**. Keep it strictly tool-agnostic until code generation; then choose a mainstream stack and justify.”

### D) “Frontend MVP — Dashboard + Prospect Card”
**Command:**  
“**Create a frontend MVP spec**: Screens and interactions for Dashboard (NBA top-5, quick actions, streaks) and Prospect Card (timeline, status, one-click logging). Provide: UI wireframes (ASCII or Mermaid), component contract (props/state), data fetching plan, and acceptance tests for ≤3-click rule. Optionally generate a minimal SPA scaffold after approval.”

### E) “End-to-End Local Dev — Make it Run”
**Command:**  
“**Assemble the runnable MVP locally**: Supply `docker-compose.yml`, environment templates, startup commands, smoke tests (`/health`, seed import, NBA returns results). Explain exactly how to run on Windows/macOS/Linux. Include rollback notes and debug tips.”

---

## 4) Acceptance & Go-Live Commands

### F) “UAT — Fill Templates & Prove the Gains”
**Command:**  
“**Run UAT with the Testpack**: Import CSVs, execute day-in-life simulation, fill `simulation/Effect_Matrix_Template.csv` and `NBA_Queue_Template.csv`. Show BEFORE/AFTER Time-to-IPA. Gate with 🟢/🟡/🔴 and list blockers + fixes if not 🟢.”

### G) “Go-Live Checklist & Cutover Plan”
**Command:**  
“**Produce a Go-Live package**: (1) Go/No-Go checklist mapped to the Zero-Based Checklist; (2) monitoring plan for week 1–2 (DAU, Interactions per user/day, Task completion rate); (3) rollback triggers and steps; (4) runbooks for no-show surges, duplicates, calendar errors, queue stalls.”

---

## 5) Optional — Tool Selection (only when you’re ready)
**Command:**  
“**Tool Selection (Optional)**: Propose 2–3 concrete stacks (No-Code and Code) with costs, limits, migration paths. Map the functional spec to each step-by-step. Recommend one; then generate import scripts/recipes, automation configs, and deployment steps for that stack.”

---

## 6) What “Done” looks like (Definition of Done)
- Data model + state machine implemented exactly as in the blueprint.  
- NBA endpoint/logic returns a prioritized list that matches the rules and tie-breakers.  
- Automations for No-Show, Video, Re-engagement, IPA Coach work with real timestamps.  
- ≤ 3 clicks from Dashboard to log an action; p95 ≤ 10s to act; p95 NBA compute < 1s.  
- UAT completed with the Testpack; Effect Matrix filled; Time-to-IPA reduced by ≥ 20%.  
- Go-Live package delivered: monitoring, runbooks, rollback.

---

### Quick Start (TL;DR you can paste right now)
**1) Orchestrator:** *(paste the block from §1)*  
**2) Then reply with:**  
> “Proceed with **No-Code MVP — Relational Base + Automations** (Section 2A). Use the Testpack and fill the Effect Matrix. Gate with 🟢/🟡/🔴.”  
— **or** —  
> “Proceed with **Repo & API Scaffold — Portable Spec First** (Section 3C). Then **End-to-End Local Dev — Make it Run** (3E). Use Docker, seed with the Testpack, prove Time-to-IPA improvements.”
