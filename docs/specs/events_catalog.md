# Events Catalog (Frazer-aligned)

Core Events
- DM_STARTED: Direct message conversation started (source: ig|messenger|whatsapp|web|ads|manual).
- INVITE_SENT: Prospect invited to see information/presentation.
- VIDEO_SENT: Presentation/video link sent to prospect.
- MEETING_BOOKED: Intro/presentation booked (date/time in properties).
- MEETING_HELD: Meeting occurred.
- NO_SHOW: Prospect didn’t attend a booked meeting.
- FOLLOW_UP_DONE: A manual follow-up completed.
- JOINED_TEAM: Prospect became team member (signup).
- PURCHASED: Prospect purchased product.
- UNSUBSCRIBED: Prospect opted out.

Payload Requirements
- event_id (string, required)
- timestamp (ISO datetime, required)
- source (ig|messenger|whatsapp|web|ads|manual|other)
- customer_id (uuid, optional)
- user_id (string, optional)
- properties (object, free-form; include booking_time for meetings)
- utm (object: source, medium, campaign, content, term)
- consent (object: email, sms, messaging, terms_version)

Automation Hooks
- VIDEO_SENT → create reminders at 24h and 48h.
- NO_SHOW → create reminders at 2h and 1d; NBA “rebook”.
- INACTIVITY_7D (derived) → create reminder at 7d; NBA “reconnect”.

Notes
- Idempotency is keyed by event_id for webhook/event ingestion.
