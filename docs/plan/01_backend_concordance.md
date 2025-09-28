# Backend Concordance — What We’re Building (Advanced, Frazer‑centric)

Objective
- Derive a precise, backend‑first specification from the entire legacy corpus in `docs/raw_docs_legacy/` (MD/markdown/TXT/JSON/PDF). Ten‑pass, multi‑source concordance with emphasis on Frazer Brookes’ method, Dashboard, Kundekort, and AI automations. GDPR intentionally out of scope for now.

Authoritative Source Anchors
- Events schema: docs/raw_docs_legacy/frazer_method_blueprints/schemas/events.json
- Pipelines: docs/raw_docs_legacy/frazer_method_blueprints/crm/pipelines.json
- Long‑form system outlines: docs/raw_docs_legacy/NWM_CRM_Complete_System.markdown, docs/raw_docs_legacy/CRM_Complete_Documentation.md, docs/raw_docs_legacy/AI_Work_Order_NWM_CRM_ZeroBased.md
- Server stubs: docs/raw_docs_legacy/frazer_method_blueprints/server_stubs/* (webhooks, CAPI)
- Messages/Metrics/Flows: docs/raw_docs_legacy/frazer_method_blueprints/{messages,metrics,flows}/*
- PDF blueprints: DESCRIPTION + CODE + BLUEPRINT & FRAZERS METHOD.pdf; Affiliate Network Marketing - CRM System builder.pdf; 2 - BUILDING BLOCKS.pdf

What We’re Building (Backend View)
- A Frazer‑method CRM/OS that encodes Talk → Invite → Show → Keep Talking as a strict pipeline and event stream, powering:
  - Dashboard KPIs + ticker (no‑shows, overdue, DMO progress, NBA suggestions)
  - Kundekort (Customer Card) with inline edits, interactions, reminders, and NBA panel
  - AI automations (reminders, prioritization, coaching prompts) driven by events and status changes

Core Data Model (derived)
- Customer
  - id, name, email, phone
  - status (canonical), notes, next_action, next_action_date
  - source, handles (ig/whatsapp), country, language
  - consent_json, utm_json (stored; validation later)
- Interaction
  - id, customer_id, type (note/call/email/meeting/reminder), content, created_at, scheduled_for?, completed
- Reminder
  - id, customer_id, type (follow_up_2h|1d|24h|48h|7d), scheduled_for, completed, created_at, message
- EventLog
  - id, customer_id?, event_type (per events.json), event_data (JSON), timestamp, user_id?

Pipelines (vocabulary)
- Recruiting & Sales (pipelines.json): "New", "Qualified", "Booked", "Held", "Won", "Lost", "No‑Show", "Joined".
- Frazer terminology (docs, messages): Relationship/Invited/Video Sent/No‑Show/Follow‑up/Signed‑up/Team.
- Internal canonical (current): Lead → Relationship → Invited → Qualified → Presentation Sent → Follow‑up → SIGNED‑UP.
- Action: add bidirectional mapping so API can accept pipeline context while persisting canonical status.

Event Envelope (events.json)
- event_name ENUM: DM_STARTED | LEAD_QUALIFIED | MEETING_BOOKED | MEETING_HELD | NO_SHOW | PURCHASED | JOINED_TEAM | UNSUBSCRIBED
- Required: event_id, timestamp (ISO), optional: source (ig|messenger|whatsapp|web|ads|manual), properties, utm, consent, user/account ids.
- Use cases from flows/messages: DM‑start, Invite, Video Sent, Booked/Held, No‑Show, Follow‑up, Conversion.

AI Automations (Frazer‑aligned)
- Triggers and actions
  - Video Sent → reminders at 24h, 48h; NBA: ask feedback, move forward
  - No‑Show → reminders at 2h, 1d; NBA: rebook
  - Inactivity 7d → reminder; NBA: reconnect
  - Qualified → NBA: send presentation; set next_action
  - Presentation Sent → reminder 48h; NBA: request feedback/objections
- Safeguards: idempotency by event_id; opt‑out obeyed; rate limit on webhooks (auth TBD)

Dashboard Requirements (backend responsibilities)
- KPIs: New leads, Video sent, Booked/Held, No‑Shows, Signed‑up/Joined, Today’s/Week’s Invites & Follow‑ups, Overdue actions
- Ticker: stream of recent events (no‑show, booked, video sent), NBA suggestions, coaching prompts
- Data: aggregate endpoints for stats; queries for upcoming interactions/reminders; events filtered by type/date

Kundekort Requirements (backend responsibilities)
- Fetch details by id; list interactions; create/update/delete interactions
- Move to next stage (respect pipeline mapping); set next_action/date
- Create reminders; list overdue/due; expose per‑customer NBA
- Log significant actions as events for audit and ticker

Initial API Surface (current + to add)
- Customers: GET /api/customers[?status], GET /api/customers/:id, POST /api/customers, PUT /api/customers/:id, DELETE /api/customers/:id, POST /api/customers/:id/next-stage, GET /api/customers/stats (extend for DMO counts, no‑show, video sent)
- Interactions: GET /api/interactions/customer/:customerId, POST /api/interactions, PUT /api/interactions/:id, DELETE /api/interactions/:id, GET /api/interactions/upcoming?limit=
- Reminders (to add surface): GET /api/reminders/due, POST /api/reminders, POST /api/reminders/:id/complete
- Events (added): GET /api/events, GET /api/events/customer/:id, GET /api/events/type/:t, POST /api/events
- Webhooks (added): POST /api/hooks/dm, POST /api/hooks/capi/lead
- NBA proxy (added): GET /api/nba, POST /api/nba/analyze

Backtest Kit (to build next)
- Synthetic dataset generator (1k contacts across stages; varied sources/UTM)
- Event replay: DM → Invite → Video Sent → Booked → No‑Show/ Held → Follow‑up → Signed‑up
- Assertions: reminders created on schedule; NBA outputs present; KPI counters correct; idempotency holds under duplicate webhooks

Execution Roadmap (backend‑first, advanced)
1) Concordance artifacts
   - Generate canonical status mapping JSON (Frazer/Recruiting/Sales ↔ internal)
   - Extract event catalog (from events.json + flows/messages) with required props
2) Validation & rules
   - Add create/update validators for customers (source/handles/utm stored; syntax normalized; no GDPR scope)
   - Implement Event→Reminder rules (Video Sent, No‑Show, Inactivity 7d)
3) Stats endpoints
   - Extend /api/customers/stats with DMO counters (invites/follow‑ups today/week), no‑show/video‑sent counts, overdue actions
4) NBA cohesion
   - Per‑customer NBA endpoint aggregation; Dashboard ticker feed
5) Backtesting harness
   - Fixtures + runner; CI job to run replay and assert

Evidence Artifacts
- Auto‑generated concordance report: docs/plan/_concordance/report.json
- Frazer Method integration notes: docs/specs/frazer_method_integration.md

Notes
- This concordance intentionally omits GDPR until specifically re‑in‑scoped.
- All findings and mappings are traceable to raw sources listed above; future updates must update both mapping JSON and the acceptance tests.
