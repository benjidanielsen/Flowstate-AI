# Frazer Method Integration — Flowstate-AI (Frazer Brookes)

Summary
- Operationalize Frazer Brookes’ method: Talk → Invite → Show → Keep Talking.
- Align daily execution (DMO: 20 invites, 30 follow-ups) with Dashboard counters and streaks.
- Map Frazer statuses to internal pipeline and implement automations (reminders/NBA/coaching) accordingly.

Pipeline Vocabulary (Frazer ↔ Canonical ↔ Internal)
- Frazer examples: New/Relationship/Invited/Video Sent/Booked/No-Show/Follow-up/Signed-up/Team
- Recruiting/Sales (pipelines.json): New/Qualified/Booked/Held/Won/Lost/No-Show/Joined
- Internal (current): Lead → Relationship → Invited → Qualified → Presentation Sent → Follow-up → SIGNED-UP
- Action: add mapping module and ensure stats endpoints accept a pipeline context.

DMO & KPIs
- Daily targets: invites=20, follow_ups=30; display on Dashboard with streaks and progress.
- KPIs: New leads, Video sent, Booked/Held, No-shows, Signed-up/Joined, Follow-ups due, Pipeline health.
- Data sources: customers stats, interactions upcoming, events filtered by type, NBA recommendations.

Triggers → Automations (Frazer-specific)
- Video Sent → schedule follow-ups at 24h and 48h; NBA: “check in, ask for feedback”.
- No-Show → schedule 2h and 1d rebook reminders; NBA: “rebook intro/presentation”.
- Inactivity 7d → reminder; NBA: “reconnect with value”.
- Qualified → NBA: “send presentation” and set next_action.
- Presentation Sent → reminder (48h) and NBA: “request feedback/objections”.
- Safeguards: idempotency (event_id), consent gating, rate limits.

Kundekort Actions
- Buttons: Invite, Send Video, Book Intro/Presentation, Mark No-Show, Move to Next Stage.
- Show DMO contributions per action (increment counters) and schedule reminders if applicable.

Coaching Loop
- Daily 4–6 questions targeting consistency and focus; weekly suggestions.
- Logged as events and surfaced in Dashboard ticker.

Acceptance Criteria (excerpt)
- AC-FRAZER-001: No-show event yields two reminders (2h, 1d) and NBA “rebook”; idempotent.
- AC-FRAZER-002: Video Sent yields 24h/48h reminders; Kundekort displays pending actions.
- AC-FRAZER-003: Dashboard DMO shows invites/follow-ups progress and streaks across days.
- AC-FRAZER-004: Pipeline stats reflect mapped Frazer statuses for Recruiting/Sales.

Backtest Scenarios
- S-NoShow: DM→Invite→Booked→No-Show; assert reminders + NBA, ensure single set with duplicate webhook.
- S-Video: Invited→Video Sent; assert 24h/48h reminders and NBA suggestions.
- S-Inactivity: Relationship→7d no interaction; assert reminder + NBA reconnect.

Implementation Notes
- Add consent/utm validators; normalize sources (ig/messenger/whatsapp/web/ads/manual).
- Provide mapping JSON for status translation and use in controllers/services.
- Extend dashboard endpoints to include DMO counters and no-show/video stats.
