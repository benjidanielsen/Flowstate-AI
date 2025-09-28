# Backend Alignment Summary (from legacy docs deep scan)

This document maps the restored legacy docs under `docs/raw_docs_legacy/` to the implemented backend.

Key sources scanned:
- `frazer_method_blueprints/schemas/events.json` – canonical event envelope
- `frazer_method_blueprints/crm/pipelines.json` – recruiting/sales pipelines
- `frazer_method_blueprints/server_stubs/*` – webhook and CAPI examples
- `NWM_CRM_Complete_System.markdown` – flows, metrics, dashboard expectations
- `CRM_Complete_Documentation.md`, `AI_Work_Order_NWM_CRM_ZeroBased.md` – field expectations (consent, UTM, handles)

Backend gaps identified and addressed:
- Events ingestion endpoints aligned with events schema
- Webhook/CAPI stubs to receive external triggers
- NBA proxy endpoints to Python worker
- Customer table extended with `source`, `handle_ig`, `handle_whatsapp`, `country`, `language`, `consent_json`, `utm_json`

Next improvements (not yet implemented):
- Add consent/utm validation middleware on customer create/update
- Map pipeline stages across `pipelines.json` and internal `PipelineStatus`
- Add GDPR endpoints: export/delete customer data
- Add rate limits and auth for webhooks

