# Flowstate-AI — Utviklingsoverblikk (Øyeblikksbilde)

> Kildegrunnlag: ProjectOverview.md, Documentation_Blueprint.md, FlowstateAI_* ledende filer, FrazerMethod_* dokumenter.

## 1. Hva vi bygger (kort)
- **Produkt**: AI-først CRM/OS for nettverksmarkedsførere med tvungen Frazer Brookes-pipeline (Talk → Invite → Show → Keep Talking).
- **Kjerneleveranser**:
  - **Dashboard (Action-Board)**: DMO-mål (20 invites, 30 follow-ups, IPA), ticker med hendelser/NBA/coaching, KPI-panel.
  - **Kundekort**: Full kundestatus, AI-score, neste steg, interaksjoner, automatiske påminnelser.
  - **Automatisering**: Hendelsesdrevet påminnelser (24h/48h, 2h/1d, 7d), NBA anbefalinger, coaching-løkke.
  - **Selvforbedring**: Loggføring, backtests, feedback engine (fase 3).

## 2. Arkitektur-snapshot
- **Frontend (Action-Board)**: React/Tailwind (vite). Fokuserer på Dashboard + Kundekort.
- **Backend (Node/Express/TS)**:
  - Endepunkter: `/api/customers`, `/api/interactions`, `/api/events`, `/api/hooks/*`, `/api/nba`, (kommende) `/api/reminders`.
  - Datamodell (SQLite dev → Postgres prod): Customers, Interactions, Reminders, EventLogs.
  - Statusmapping: Frazer ↔ Recruiting/Sales ↔ intern.
- **Python Worker (FastAPI)**: NBA/Reminder-prosessering (skal orkestrere kjørt logikk fra backend).
- **Testing**: Jest (backend), Vitest (frontend), planlagt backtest-rigg.

## 3. Nåværende status i repo (etter fase 1)
- Hendelses-API, webhooks (DM, CAPI) og NBA-proxy implementert.
- Kundetabell utvidet med kilde/handles/UTM (validering gjenstår).
- Dokumentasjon: `00_master_plan.md`, `01_backend_concordance.md`, `frazer_method_integration.md` etablert.

## 4. Umiddelbar utviklingsramme (backend først)
1. **Kanoniske artefakter** (pågående)
   - `specs/canonical_spec.yaml`, `specs/glossary_and_mappings.md`, `specs/events_catalog.md` (fra ledende filer).
2. **Regler & validering**
   - Valider `source/handles/utm` ved kundes opprettelse/oppdatering.
   - Implementer Event→Reminder-oppsett: Video Sent (24h/48h), No-Show (2h/1d), Inaktivitet 7d.
3. **Statistikk & DMO**
   - Utvid `/api/customers/stats` med DMO-tellere (dag/uke), no-show/video-sent, IPA-progress.
4. **Stage-mapping**
   - Modul for Frazer/Recruiting/Sales ↔ intern status + API-støtte.
5. **Backtest-harness**
   - Fixtures + replay (DM→Invite→Video→Booked→No-Show/Held→Follow-up→Signed-up) med idempotens.

## 5. Plan for videre (fra Documentation_Blueprint)
- **Unified README** (definitiv kilde): bygge etter at kanoniske artefakter er klare.
- **Risiko/avvik**: Liste opp kjente hull (AI-loop, forbedringsmotor, sikkerhet) og markere «v2».
- **Selv-audit**: Etter hver milepæl kjøre check mot krav fra FlowstateAI_UnifiedSystemDesign og QA-dokumenter.

## 6. Akutte oppgaver («Start utvikling nå»)
- [ ] Fullfør kanonisk spesifikasjon + begrepsmapping (backend team sync).
- [ ] Legg til inputvalidering i `customerController`/`customerService` (Joi-skjema for kilde/UTM/handles).
- [ ] Event→Reminder-regler + nye endepunkter for reminders (create/list/complete).
- [ ] Utvid stats-controller med DMO tellere og pipeline mapping.
- [ ] Sett opp `tests/backtest_plan.md` + første fixtures (JSON) og skript.
- [ ] Oppdater Developer FAQ/Tech QA når ovenstående er klare (versjonsnotat).

## 7. Kommunikasjon & sporbarhet
- Alle nye spesifikasjoner inn i `docs/specs/*` (referanse i README-plan).
- PR-/commit-meldinger skal referere til krav-ID (fra UnifiedSystemDesign) + AC (fra frazer_method_integration).
- QA-iterasjoner følger `FlowstateAI_QA_Testing_Iteration.md` – logg i `docs/tests/run_log.md` (opprettes ved første kjøring).

## 8. Neste steg (foreslått rekkefølge)
1. Kanonisk spesifikasjon + mapping (dokumentasjon).
2. Backend validering + reminder-regler (kode + tester).
3. Stats/DMO-endepunkt + pipeline mapping.
4. Backtest rigg + kjøring.
5. Unified README v1 (etter at alt over er dekket).

