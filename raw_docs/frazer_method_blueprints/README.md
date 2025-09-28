# FRAZER METHOD – Vendor‑Agnostic Blueprints (EXAMPLES ONLY)

**Viktig:** Dette er *rene eksempler på struktur og byggeklosser*. 
En **annen AI** eller utvikler vil bygge det faktiske systemet og **trenger ikke** bruke de appene som er nevnt tidligere. 
Poenget her er å vise *hvordan* du kan gjøre det **uansett verktøy** (egen kode, andre plattformer, etc.).

Bruk dette som en **mal**: hendelsesnavn, objekter, flows, API‑payloads, agentroller, felt og målepunkter.
Alt kan mappes til hvilket som helst CRM, DM‑plattform, kalender, iPaaS eller annonse‑API.

Generert: 2025-09-25

## Mappeinnhold
- `schemas/` – kanoniske JSON‑skjema for events og CRM‑objekter.
- `flows/` – *vendor‑agnostiske* automasjons‑eksempler (Make/n8n/Pipedream/Zapier) + server‑side Conversions mapping.
- `ai/` – RAG‑pipeline og multi‑agent roller (YAML) + prompt‑tips.
- `crm/` – pipeline/felter som kan mappes til hvilket som helst CRM.
- `consent/` – GDPR‑retningslinjer og samtykkemodell.
- `metrics/` – KPIer/funnel definert mot eventene.
- `sql_dbt/` – eksempelmodeller (dbt‑stil) for å bygge et enkelt datamart.
- `server_stubs/` – små kode‑stubber (Python/JS) for webhooks/CAPI.
- `messages/` – DM/epost‑maler med variabler.

## FRAZER flyt (innhold → DM → kvalifisering → booking → møte → kjøp/join → duplisering)
1) Innhold/annonse utløser **DM**.  
2) **Kvalifisering** (3–5 spørsmål) + eksplisitt **samtykke**.  
3) **Opprett/Ruter** kontakt & sak/deal; gi **bookinglenke** umiddelbart.  
4) **Oppfølging** (no‑show/win‑back) og **onboarding/duplisering** via mikroleksjoner.  
5) **Mål** alt med server‑side events og funnel‑analyse.

> Tips: Bruk `event_id` / `external_id` for **idempotens** (unngå duplikater ved retries).
