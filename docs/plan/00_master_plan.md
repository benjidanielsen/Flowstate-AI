# Flowstate‑AI — Plan on the Plan (Advanced Concordance)

Purpose
- Assemble every requirement spread across legacy raw docs into a single master plan of plans.
- Create a traceable path from notes → canonical spec → scoped workstreams → tests/backtests → operating guardrails.
- Keep Dashboard, Kundekort (Customer Card), and AI Automations as first‑class pillars.

Scope of Inputs (deep scan sources)
- docs/raw_docs_legacy/** (all files): blueprints, pipelines, events schema, messages, metrics, stubs, and long‑form notes.
- Priority anchors used for cross‑checking:
  - frazer_method_blueprints/schemas/events.json
  - frazer_method_blueprints/crm/pipelines.json
  - frazer_method_blueprints/metrics/metrics_kpis.md
  - frazer_method_blueprints/messages/*.md
  - frazer_method_blueprints/server_stubs/* (webhooks, CAPI)
  - NWM_CRM_Complete_System.markdown
  - CRM_Complete_Documentation.md
  - AI_Work_Order_NWM_CRM_ZeroBased.md

Core Concepts (consolidated)
- Dashboard: goals (20 invites/30 follow‑ups), KPI tiles, pipeline stats, ticker (alerts + AI insights), daily/weekly progress.
- Kundekort: inline editable customer card; status (pipeline), contact details, next action/date, interaction history, reminders, NBA suggestions.
- Events: typed envelope (event_name, event_id, timestamp, source, properties, consent, utm, user/account ids).
- Pipelines: Recruiting and Sales stage vocabularies; internal canonical statuses; bi‑directional mapping.
- Interactions & Reminders: logging touchpoints; automated follow‑ups (2h/1d/24h/48h/7d) for video sent, no‑show, inactivity.
- AI Automations: NBA recommendations, prioritization, coaching prompts, feedback/improvement loop.
- Consent & GDPR: store and enforce preferences; export/delete flows; audit via event logs.

Deliverables (artifacts to produce)
- Canonical Spec: docs/specs/canonical_spec.yaml
- Domain Glossary & Mappings: docs/specs/glossary_and_mappings.md
- Requirements Matrix (traceability): docs/specs/requirements_matrix.csv (doc → requirement → user story → test → code path)
- Dashboard Spec: docs/specs/ui_dashboard.md (widgets, KPIs, ticker events)
- Kundekort Spec: docs/specs/ui_kundekort.md (fields, actions, validations, reminders)
- Automation Rules: docs/specs/ai_automations.md (triggers → actions, idempotency, safeguards)
- Event Tracking Plan: docs/specs/events_tracking_plan.md (event catalog + required properties)
- GDPR Guardrails: docs/specs/gdpr_guardrails.md (consent, export/delete, retention)
- Backtest Plan & Fixtures: docs/specs/backtest_plan.md, data/fixtures/*.json

Plan on the Plan (multi‑layer roadmap)
1) Concordance Build (Truth Synthesis)
   - Index and tag every statement in legacy docs (topic: Dashboard/Kundekort/Events/Pipelines/AI/GDPR/Metrics/Flows).
   - Extract conflicts and synonyms; propose canonical names (e.g., Signed‑up vs Joined).
   - Output: canonical_spec.yaml + glossary_and_mappings.md.

2) Requirements Matrix + Acceptance Criteria
   - Derive atomic requirements with IDs (REQ‑DASH‑001, REQ‑CARD‑004, REQ‑AI‑012…).
   - Attach acceptance tests per requirement (Given/When/Then + metrics).
   - Output: requirements_matrix.csv.

3) Baseline System Alignment (Now → Canonical)
   - Backend: ensure schema matches canonical Customer/Interaction/Reminder/Event; add consent/utm enforcement.
   - Worker: ensure NBA endpoints and reminder engine align to rules (durations, escalation, idempotency).
   - Frontend: Dashboard and Kundekort views expose the canonical fields and actions.
   - Output: diffs and migration notes.

4) Advanced Features & Automations
   - Pipeline bridge: map Recruiting/Sales stage sets to internal statuses; APIs to set/get stage with pipeline context.
   - AI scoring/prioritization: compute A/B/C and urgency; surface NBA in Dashboard ticker and Kundekort panel.
   - Coaching loop: daily prompts/questions + weekly focus suggestions; log via event_logs for improvement engine.

5) Backtesting & Error Checks (Evidence)
   - Synthetic cohort generator: create 1k contacts across stages with interaction patterns and consent mixes.
   - Event replay rig: DM→Invite→Video Sent→No‑Show/Attended→Follow‑Up chains; assert reminder creation and NBA outputs.
   - KPI validation: dashboard counts, conversion rates, overdue follow‑ups; time‑based assertions.
   - Data quality gates: event schema validation, consent gating, UTM normalization, idempotency checks.
   - Output: backtest_plan.md + fixtures + automated tests.

6) Governance & Observability
   - Structured logging (request id, event id), rate limits on webhooks, API keys/JWT.
   - GDPR endpoints: export/delete by customer; audit events.
   - Improvement engine: capture feedback and auto‑create developer reports.

Dashboard — Detailed Plan
- KPIs: New leads, Video sent, Webinar booked/held, No‑shows, New customers/team, Follow‑ups due, Pipeline health.
- Ticker: alerts (no‑shows, overdue actions), quotes, AI insights (e.g., 60% IPA), NBA recs.
- Graphs: status flow, win/loss, 90‑day trend, IPA target progress.
- Data sources: /api/customers/stats, /api/interactions/upcoming, /api/events?filters, /api/nba.
- Edge cases: empty states, high‑volume pagination, timezone consistency.

Kundekort — Detailed Plan
- Fields: name, email, phone, status (pipeline), notes, next_action(+date), consent, utm, platform handles.
- Interactions: list/create/update/delete; types (note/call/email/meeting/reminder); completed flag.
- Reminders: create due reminders; show overdue; quick actions.
- NBA Panel: per‑customer recommendations (title/description/priority/urgency).
- UX: inline edit; status badges with color; safe navigation on error/missing entity.

AI Automations — Detailed Plan
- Triggers: Video Sent, No‑Show, Inactivity (7d), Presentation Sent, Qualified.
- Actions: schedule reminders (2h/1d/24h/48h/7d), generate NBA items, adjust priorities.
- Safeguards: idempotency key (event_id), consent checks, opt‑out respect, rate‑limit.
- Evaluation: coverage of triggers; correctness of next_action generation.

Traceability Map (seeds)
- Events schema → /api/events (create/list) and event_logs table.
- Pipelines.json → status mapping module (to be added) + stats endpoint.
- Metrics KPIs → dashboard KPIs and queries.
- Server stubs → /api/hooks/dm and /api/hooks/capi/lead.
- Messages → templates for reminders (to be linked).

Backtest Scenarios (initial set)
- S1: DM started → Invited → Video Sent → No‑Show → Reminders (2h → 1d) created; NBA suggests “rebook”.
- S2: Qualified → Presentation Sent → Follow‑up → Signed‑up; KPI counters update.
- S3: Inactivity 7d → reminder + NBA “reconnect”; consent false → no reminder created.
- S4: Duplicate webhook with same event_id → idempotent, single event/reminder.

Next Actions
- Generate draft canonical_spec.yaml and glossary_and_mappings.md from sources.
- Build requirements_matrix.csv (doc‑driven) and link to code paths.
- Implement consent/utm validation on customer create/update.
- Add pipeline mapping module and extend stats endpoint.
- Stand up backtest fixtures and a test runner script.

