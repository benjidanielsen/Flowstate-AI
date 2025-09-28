# **AI \+ CRM (MODERN)**

Alt under er **rene, leverandør-agnostiske eksempler** på struktur og byggeklosser. En annen AI kan bruke idéene, eventnavnene, feltene og flytene her for å bygge systemet sitt med **hvilke som helst** verktøy eller helt egen kode.

# **Hva du får (kun eksempler på struktur)**

* **Schemas** (JSON): kanoniske *events* og *CRM-objekter* (enkelt å mappe til hvilket som helst CRM).

* **Flows** (Make / n8n / Pipedream / Zapier – vendor-agnostiske):  
   Comment→DM→Kvalifisering→CRM upsert→Booking→Varsling→Server-side *Conversions* \+ egen **No-show→Rebook**.

* **AI** (YAML): RAG-pipeline \+ tre agent-roller (lead\_triage, follow\_up\_coach, duplication\_coach) med guardrails og prompts.

* **CRM**: generiske pipeline-steg og felter som kan mappes til hva som helst.

* **Consent/GDPR**: samtykkemodell og vakter (gating av events).

* **Metrics/KPI**: definert mot eventene (DM→Qualified→Booked→Held→Purchase/Join).

* **SQL/dbt**: små modeller som viser hvordan et lite datamart for funnel kan se ut.

* **Server-stubber**: Python (Flask) og Node/Express webhooks \+ CAPI endepunkt (skjelett).

* **Meldingsmaler**: kvalifisering og no-show (variabel-vennlig).

# **Eksempel fil**

Fil blueprint-pakken (ZIP)   
Filnavn: “frazer\_method\_blueprints.zip”

# **Hvordan bruke (eksempel, ikke fasit)**

* **Bygg din egen stack:** Map `schemas/` til dine felter/tabeller. Portér en av `flows/` til ditt orkestreringsverktøy (eller egen kode).

* **AI-laget:** Fyll `ai/` med dine SOP/FAQ/komp-plan-dokumenter, bytt ut `YOUR_VECTOR_DB` / `YOUR_EMBEDDING_MODEL` og koble agentene til dine verktøy.

* **Måling:** Kopier `sql_dbt/` mønsteret uansett hvilket lager/ORM du bruker; viktigst er event-navn og idempotens (`event_id`).

* **Personvern:** Bruk `consent/gdpr_guardrails.md` som “sjekkliste” når du porter til andre APIer.

# 

# **FREMGANGSMÅTE AV ET ANNET SYSTEM MED FORSKJELLIG VERKTØY:**

**AI-drevet CRM-system for Network Marketing med automasjon**, bygget på “DESCRIPTION \+ CODE \+ BLUEPRINT” og “FRAZER METHOD” (DM-først, kvalifisering, oppfølging, duplisering).

3 \- BUILDING BLOCKS

Nedenfor er den **beste, pragmatiske stakken** plukket fra listen du sendte—ordnet i “kjerne → lim → måling → AI → støtte”. Jeg forklarer hvorfor hver passer perfekt til *FRAZER-flyten* (innhold → DM → kvalifisering → booking/kjøp → onboarding/duplisering).

# **Kjerne**

1. **CRM: HubSpot** (evt. **Pipedrive** hvis du vil være ultralett; **GoHighLevel** hvis du vil white-labele og duplisere konto-maler til downline)  
    **Hvorfor:** HubSpot gir rask utrulling, sterke **Workflows**, sekvenser, bra API og skalerer fra SMB til enterprise. Nettverksmarkedsføring trenger strømlinjet *lead→deal→kunde→recruit* med én sannhetskilde og enkel rapportering.  
    **Hvordan:** Én pipeline for *Recruiting*, én for *Sales/Orders*. Required fields på stage-endringer, automasjoner for oppfølging, og egne **Team/Owner**\-felter for upline/downline routing.

2. **DM/Chat: Manychat (IG/Messenger)**  
    **Hvorfor:** “FRAZER-metoden” er DM-først. Manychat gir **comment→DM**, story-mentions, nøkkelord og webhooker. Perfekt for “post → DM → kvalifisering”.  
    **Hvordan:** Flow: *Kommentar “guide”* → auto-DM (samtykke) → 3 kvalifiseringsspørsmål → webhook → CRM-kontakt \+ stage → send bookinglenke.

3. **Booking: Cal.com (+ Chili Piper ved inbound lead-ruting)**  
    **Hvorfor:** Cal.com er multi-brand, OS og kan selvhostes (EU-vennlig). Chili Piper konverterer MQL til møte *med én gang*.  
    **Hvordan:** Routing forms i Cal.com (budsjett/land/produkt) → riktig rådgiver/team. Logg booking \+ “no-show” tilbake til CRM.

4. **Marketing Automation: ActiveCampaign** (evt. **Brevo** for EU-budsjett; **Klaviyo** hvis e-handel er tungt)  
    **Hvorfor:** Du får kraftige e-post/SMS-flows uten kompleks enterprise-oppsett.  
    **Hvordan:** “Welcome/Nurture”, “Abandoned Checkout/Call”, “Post-purchase/Onboarding”, “Win-back”. Bruk **tags**/goals som enkel state-maskin.

# **Lim (integrasjon)**

5. **iPaaS: Make (EU) \+ Pipedream (dev-webhooks)**  
    **Hvorfor:** Make gir visuelle scenarier, EU-databehandling og hundrevis av konektorer; Pipedream gir deg kjapp kode rundt sær-APIer.  
    **Hvordan:** **Manychat Webhook → Make**: opprett kontakt i HubSpot, post **Cal.com**\-lenke, send **Slack**\-varsel, trigge **ActiveCampaign**\-flow, og skyt **Meta CAPI** server-event (Lead/Schedule).

# **Måling & annonser**

6. **Meta Conversions API (+ Pixel)**  
    **Hvorfor:** Stabil attribusjon når cookies ikke holder. Kritisk for å vite hvilke Reels/DM-hooks som faktisk gir leads og bookinger.  
    **Hvordan:** Send `event_id` \+ `fbp/fbc` fra Make; map `content_ids/value/currency`; respekter samtykke.

7. **Mixpanel (produkt/growth)** \+ **Segment** (CDP) når du vil stramme inn event-skjema  
    **Hvorfor:** Du vil se *Content → DM → kvalifisert → Booket → Holdt møte → Kjøp/Join* som en funnel og bygge kohorter for win-back/VIP.  
    **Hvordan:** Spesifiser events: `DM_Started`, `Lead_Qualified`, `Meeting_Booked`, `Meeting_Held`, `Joined_Team`, `Made_Purchase`. Synk kohorter til e-post/annonser.

# **AI-laget**

8. **LangChain \+ LlamaIndex** (+ valgfri hosting på **Vertex AI** om du vil ha GCP-governance)  
    **Hvorfor:** RAG-assistenter som *forstår dine scripts, SOPer, produktark og komp-plan*—akkurat det “DESCRIPTION \+ CODE \+ BLUEPRINT” sikter mot.  
    3 \- BUILDING BLOCKS

    **Hvordan:**

* **Ingest:** SOPer, tilbud, compliance-regler, produkt-FAQ → vektorindeks.

* **Agent 1 (Lead Triage):** Les kvalifiseringssvar fra Manychat, foreslå neste steg \+ mal (godkjennes i Slack/CRM).

* **Agent 2 (Follow-up Coach):** Generér personaliserte DM/e-poster basert på persona, språk og historikk.

* **Agent 3 (Duplication Coach):** Onboarding-mikroleksjoner og sjekklister for nye partnere—i DM/e-post.

# **Støtte**

9. **Airtable \+ Notion \+ Slack**  
    **Hvorfor:** Airtable som “operativ lett-DB” (team, scripts, content-bank), Notion som kunnskapsbase/dupliserbar playbook, Slack som operativ nerve (varsler, Godkjenn/Avvis).  
    **Hvordan:** Airtable “Template Library” for DM-hooks, Notion “Team Hub” med FRAZER-DMO (Daily Method of Operation), Slack-varsler ved nye MQL/No-show/VIP.

---

## **“Golden path” (slik henger det sammen)**

1. **IG Reels → kommentar “guide”** → *Manychat* starter kvalifisering (opt-in).

2. **Webhook (Make)** → opprett **HubSpot**\-kontakt \+ sett *Recruiting/Sales* pipeline-stage.

3. Send **Cal.com**\-lenke (+ **Chili Piper** hvis inbound skjema) → logg booking.

4. Skyt **Meta CAPI** event (*Lead/Schedule*).

5. **Slack**: “Ny kvalifisert lead for \[Brand\] — foreslått mal-svar” (fra **LangChain/LlamaIndex**).

6. **ActiveCampaign**: Nurture/No-show/Win-back flows.

7. **Mixpanel**: Funnel fra DM→Booking→Holdt møte→Kjøp/Join; kohorter synkes til e-post/annonser.

8. **Notion/Airtable**: Onboarding-sjekklister \+ delbare “dupliser-dette” maler.

---

## **Hvorfor disse – direkte mot *FRAZER METHOD***

* **DM-først & duplisering:** Manychat (+ Notion maler) gjør at nye partnere kan kopiere vinnende DM-hooks på minutter.

* **Hastighet til handling:** Chili Piper/Cal.com fjerner friksjon fra MQL→møte.

* **Automatisk coaching:** LangChain/LlamaIndex gir “AI som lærer AI” over dine scripts/SOPer—replikerer beste praksis til hele teamet.

* **Synlig ROI:** Meta CAPI \+ Mixpanel viser hvilke innholdsbiter/DM-flows som faktisk flytter folk til booking/kjøp.

* **EU-hensyn:** Make (EU), Cal.com self-host mulighet, dataminimering, og tydelig opt-in i Manychat/ActiveCampaign.

---

## **Minimal start (uke 1–2)**

* **HubSpot \+ Manychat \+ Make \+ Cal.com \+ ActiveCampaign \+ Slack**  
   Konfigurer 3 flows: *Comment→DM*, *DM→Booking*, *No-show→ny booking*.  
   Events til **Mixpanel** for enkel funnel.

## **Nivå 2 (måned 1–2)**

* **Meta CAPI** live, **Notion** playbook, **Airtable** content/scripthub, AI-assistenter (LangChain+LlamaIndex).

## **Nivå 3 (måned 3+)**

* **Segment** som CDP, **Hightouch** for annonser/CRM-aktivering, ev. **Vertex AI** for enterprise drift.

# **DETTE ER VERKTØY FUNNET ONLINE OG BESKREVET AV CHATGPT:** 

Gruppert ALLE de 110 fra lista di i relevante kategorier og rangert dem **innenfor hver kategori** (øverst \= mest nyttig/bred/robust for ditt bruk: Norge/EU, flere brands, Meta/IG, SMB/agency). Hver får én kort beskrivelse.

**Legend:** (OS) \= open-source • (E) \= enterprise • (SMB) \= små/mellomstore

---

# **Bonus: Mest sannsynlige “kjernevalg” (hurtig anbefaling av ChatGPT)**

* **CRM:** HubSpot *eller* Pipedrive (evt. GHL for alt-i-ett byråstil).

* **Booking:** Cal.com \+ (Chili Piper hvis lead-ruting er kritisk).

* **DM/Chat:** Manychat (IG/Messenger) \+ Intercom på web.

* **iPaaS:** Make (EU) \+ Pipedream for dev-webhooks.

* **Måling:** Meta CAPI \+ Mixpanel \+ (Segment/Hightouch når datalager kommer).

* **AI/Agents:** LangChain \+ LlamaIndex for SOP/FAQ/triage.

* **Prosjekt/DB:** Notion/Airtable \+ Slack-varsler.

#  

# **CRM & Revenue-plattformer**

## **Salesforce Sales Cloud (E)**

* **Kjernefunksjoner:** Accounts/Contacts/Leads/Opportunities, Forecasting, CPQ (tillegg), Flow Builder, Apex, AppExchange, Einstein-innsikt.

* **Best på:** Kompleks enterprise-salg, compliance, skreddersøm i stor skala.

* **Hvorfor/hvordan:** Bygg prosesser i **Flow** (ikke bare triggers), hold tilpasning i metadata/appar, og bruk AppExchange for standardbehov før kode. Koble til ERP/Marketing Cloud for “lead-to-cash”.

  ## **HubSpot (SMB→E)**

* **Kjerne:** CRM \+ Hubs (Marketing/Sales/Service/Operations), Workflows, Sequences, landingssider, rapporter, bra API/Marketplace.

* **Best på:** Rask iverksetting, alt-i-ett go-to-market, innholds-/inbound-drevet vekst.

* **Hvorfor/hvordan:** Start “Hub-lett” (Sales/Marketing Pro), modeller pipelines og obligatoriske felter, bruk **Workflows** for lead-routing/score, og hold e-post/SMS i HubSpot for sporbarhet.

  ## **Microsoft Dynamics 365 Sales (E)**

* **Kjerne:** Leads/Opportunities, Forecast, Playbooks, (CPQ via partner), tett med **Power Platform**, Dataverse, Teams/Outlook.

* **Best på:** Microsoft-stack, sikkerhet/governance, modell-drevne apper.

* **Hvorfor/hvordan:** Bruk **Power Automate** for flyter, **Power BI** for salgspulser, og Dataverse-tabeller for delt datamodell. Knytt inn **Customer Service** og **Field Service** ved behov.

  ## **Zoho CRM (SMB)**

* **Kjerne:** Moduler, **Blueprint** (prosessmotor), Workflows, Omnikanal, Zia-AI, rimelig lisens, Zoho One-økosystem.

* **Best på:** Kost/nytte for SMB med bred app-portefølje (CRM \+ Desk \+ Campaigns \+ Books).

* **Hvorfor/hvordan:** Tegn salgsprosess i **Blueprint**, la **Zoho Flow** binde apper, og bruk **Desk**/**Campaigns** for kundereise uten å forlate Zoho.

  ## **Pipedrive (SMB)**

* **Kjerne:** Visuell pipeline, Aktiviteter, E-postsync, Automations, Insights, markedsplass-apper.

* **Best på:** Fokusert, enkel salgsutførelse og høy “rep-adopsjon”.

* **Hvorfor/hvordan:** Definér 1–2 pipeliner med få, tydelige steg og “required fields on stage change”. Koble automasjoner til e-post/SMS og bruk **Insights** for win-rate/aging.

  ## **Freshsales (SMB)**

* **Kjerne:** 360-kontakt, innebygd telefoni/SMS, Sequences, **Freddy AI**, tett med Freshdesk.

* **Best på:** Salg \+ support i samme familie (Freshworks-suite).

* **Hvorfor/hvordan:** Synk support-tags fra **Freshdesk** inn i lead score; kjør ringe-/sekvens-playbooks fra Freshsales for “speed-to-lead”.

  ## **GoHighLevel (SMB/agency)**

* **Kjerne:** CRM, funnels/landingssider, e-post/SMS/WhatsApp (via Twilio/LC), kalender, call tracking, reputation, white-label & snapshots.

* **Best på:** Byråer/nettverkssalg som trenger alt-i-ett og gjenbrukbare “konto-maler”.

* **Hvorfor/hvordan:** Lag **Snapshots** per brand/niche, koble **LC Phone/Twilio**, og bygg DM→pipeline→booking-flows. Vær nøye på GDPR/SMS-samtykke.

  ## **Close (SMB/inside sales)**

* **Kjerne:** Innebygd dialer (power/predictive), SMS/e-post-sekvenser, pipeline, call-opptak.

* **Best på:** Telefon-tungt “inside sales” (SaaS/B2B) med høyt volum.

* **Hvorfor/hvordan:** Design korte, stramme sekvenser (e-post+ring+SMS), bruk **Call Dispositions** og **Custom Fields** for coaching/rapport.

  ## **Copper (SMB/Google)**

* **Kjerne:** Dyp **Gmail/Calendar/Drive**\-integrasjon, Deals, Tasks, automatisk e-postfangst.

* **Best på:** Google-først-team som vil jobbe **inne i Gmail**.

* **Hvorfor/hvordan:** Tren teamet til å leve i sidepanelet i Gmail/Calendar; bruk **Google Sheets**\-sync for lette rapporter.

  ## **Keap (SMB)**

* **Kjerne:** CRM \+ **Campaign Builder** (drag-and-drop), e-handel (tilbud/faktura), e-post, booking.

* **Best på:** Småbedrifter som trenger enkel “lead→kunde→betaling” i ett system.

* **Hvorfor/hvordan:** Start med 1–2 **Campaigns** (lead nurturing \+ post-purchase), bruk innebygd checkout/tilbud for kortere salgssyklus.

  ## **LeadSquared (SMB)**

* **Kjerne:** Marketing-automatisering \+ **Sales Execution**, lead-distribusjon/score, mobil-CRM for feltteam, telephony-connect.

* **Best på:** Høy “speed-to-lead”, felt-/inside-hybrid (edtech, helse, finans).

* **Hvorfor/hvordan:** Sett **assignment rules** (region/skill), bruk mobil-appen for sjekk-inn/geotags, og bygg SLA-varsler når lead ikke kontaktes i tide.

  ## **SAP Sales Cloud (E)**

* **Kjerne:** Del av SAP CX; Lead→Opportunity, **Guided Selling**, **CPQ**, felt-salg, tett med S/4HANA.

* **Best på:** SAP-miljøer, komplekse tilbud/pris (CPQ) og global styring.

* **Hvorfor/hvordan:** Bruk **SAP Integration Suite (CPI)** mot ERP; standardiser produkt/kundemaster i SAP og la Sales Cloud håndtere prosess/CRM.

  ## **Odoo (ERP/CRM)**

* **Kjerne:** Modulært ERP (CRM, Salg, Faktura, Lager, Prosjekt), **Studio** for tilpasning, nettside/marketing-apper.

* **Best på:** SMB som vil ha **én** plattform for drift \+ salg.

* **Hvorfor/hvordan:** Start “lean” (CRM+Salg+Faktura), unngå tung koding; bruk **Studio** til felter/visninger/automatisering og hold deg til kjerne-moduler.

  ## **SugarCRM (SMB→E)**

* **Kjerne:** Sugar Sell/Serve, **SugarPredict** (AI), Studio-tilpasning, avanserte rapporter/BPM, fleksibel hosting.

* **Best på:** Tilpasningsbehov \+ kontroll (inkl. privat hosting).

* **Hvorfor/hvordan:** Modeller prosesser i **Advanced Workflow**, hold tilpasning i **Studio/Module Loader**, og koble BI for forecasting.

  ## **SuiteCRM (OS)**

* **Kjerne:** Open-source fork av Sugar, moduler, workflows, **REST API**, selvhost (LAMP).

* **Best på:** Null lisenskostnad, full kontroll, tung skreddersøm.

* **Hvorfor/hvordan:** Planlegg drift/oppdateringer og sikkerhet; bygg egne moduler/felter via Studio, og legg integrasjoner på **API** \+ køtjeneste (f.eks. RabbitMQ/Redis).

1. 

---

# **Sales Engagement, Prospecting & Revenue Intelligence**

## **Outreach**

* **Kjerne:** Cadences (e-post/oppgaver/anrop), A/B-testing, regler/SLA, CRM-sync, rapporter.

* **Best på:** Skalerbar, styrt outbound for SDR/AE i B2B.

* **Hvorfor/hvordan:** Bygg 3–5 ICP-spesifikke cadences, håndhev “speed-to-lead” med SLA-varsler, la CRM være “source of truth”, bruk rapportene til å kutte svake steg og doble på det som virker.

  ## **Salesloft**

* **Kjerne:** Multikanal-sekvenser, innebygd dialer, call-coaching, cadences, rapporter.

* **Best på:** Call-tunge team og praktisk coaching i flyt.

* **Hvorfor/hvordan:** Lag korte, stramme sekvenser (e-post+ring+LI-oppgave), bruk **call dispositions** \+ snippets for coaching, evaluer “connect→meeting” pr. rep/sekvens ukentlig.

  ## **Apollo.io**

* **Kjerne:** B2B-databank (firma/kontakt), berikelse, e-postsekvenser, intent-/teknografifiltre.

* **Best på:** Én pakke for listebygging \+ outbound i SMB/mid-market.

* **Hvorfor/hvordan:** Definér ICP (bransje, størrelse, tech-stack), bygg lister, berik CRM, kjør sekvenser fra Apollo eller push til Outreach/Salesloft; hold streng hygiene (bounces, validering).

  ## **LinkedIn Sales Navigator**

* **Kjerne:** Avansert søk, lagrede lister, varsel/signaler, TeamLink.

* **Best på:** Målrettet ABM/prospektering—ikke automatisering.

* **Hvorfor/hvordan:** Lag “Named Accounts”, følg signaler (job-change, headcount), legg LI-oppgaver inn i cadences som manuelle steg; unngå uoffisielle automasjons-bots (risiko for sperring).

  ## **Reply.io**

* **Kjerne:** Multikanal (e-post, anrop, LI-oppgaver), sekvenser, enkel dialer, rapporter.

* **Best på:** Rimelig, fleksibel outbound i SMB.

* **Hvorfor/hvordan:** Sett kapper (daglige send, pauser), varm opp domener, bruk **conditional branches** (åpnet/ikke åpnet), synk toveis med CRM.

  ## **Lemlist**

* **Kjerne:** Kald e-post \+ sterk bilde/video-personalisering, warm-up, sendings-infrastruktur.

* **Best på:** Høy svarrate via dynamiske bilder/vids (“icebreakers”).

* **Hvorfor/hvordan:** Bygg maler med dynamiske felter/bilder, bruk eget tracking-domene, ramp sendvolum gradvis, test 1 variabel om gangen (subj vs. åpningslinje).

  ## **Instantly.ai**

* **Kjerne:** Masse-skala kald e-post, multi-innbokser, rotering, warm-up, deliverability-score.

* **Best på:** Outbound i stor skala (byrå/aggregert volum).

* **Hvorfor/hvordan:** Rotér 5–20 innbokser pr. kampanje, sett konservative sendekvoter (30–50/dag/inbox i start), overvåk bounces/complaints, hold lister ultrarene.

  ## **Gong**

* **Kjerne:** Samtaleintelligens (opptak→transkripsjon→innsikt), deal boards, coach-analyser.

* **Best på:** Coaching i stor skala \+ “reality-based” forecasting.

* **Hvorfor/hvordan:** Slå på opptak over Zoom/dialer, lag **trackers** for konkurrenter/tema, bygg “call library” med beste anrop, kjør ukentlig deal-review direkte i Gong.

  ## **Chorus (ZoomInfo)**

* **Kjerne:** Call-analyse/coaching, tematikk, snakkeforhold, biblioteker; tett med ZoomInfo-data.

* **Best på:** Team som allerede bruker ZoomInfo for prospektering/intent.

* **Hvorfor/hvordan:** Lag playlister per fase (discovery/demo/negotiation), standardiser “next steps”-språk og mål talk-time pr. persona.

  ## **Clari**

* **Kjerne:** Forecasting, pipeline-helse, risikoflagg, dekning/konverterings-innsikt.

* **Best på:** Forutsigbarhet på tvers av team/regioner/kvartaler.

* **Hvorfor/hvordan:** Koble CRM \+ kalender/e-post, definer stage-definisjoner og **commit/best case**, mål **pipeline coverage** (3–5× mål), bruk “inspect” ukentlig for å fjerne zombie-deals.

  ## **Chili Piper**

* **Kjerne:** Inbound lead-ruting \+ øyeblikkelig booking fra skjema/DM, round-robin, kvalifisering.

* **Best på:** Konvertere MQL/handraiser til møte på sekundet.

* **Hvorfor/hvordan:** Embed på skjema (HubSpot/Marketo), rutér på territorium/vertikal, book direkte i AEs kalender, SMS/e-post-påminnelser, mål “form submit → meeting held”.

---

# **Marketing Automation & Kundereiser**

## **Adobe Marketo Engage (E)**

* **Kjerne:** Engagement Programs, Smart Campaigns, lead score, avansert segmentering, flåtestyring, program-templat, Salesforce/Adobe-økosystem.

* **Best på:** Enterprise nurture/ABM i stor skala med streng governance.

* **Hvorfor/hvordan:** Standardiser **program-maler** (tokenized), definer **program statuses** per kanal, la **Smart Lists** håndtere segmentlogikk, og bygg MQL med **behaviour \+ firmografisk score**. Bruk **Workspaces/Partitions** for flere brands/land.

  ## **Braze (E)**

* **Kjerne:** Omnikanal (push, e-post, SMS, WhatsApp, in-app, Content Cards), **Canvas Flow** (journeys), real-time events, Liquid-personalisering, frekvens-/quiet hours.

* **Best på:** App-/produktdrevne kundereiser med høy personalisering i sanntid.

* **Hvorfor/hvordan:** Start med 3 kjerne-canvases: **Onboarding**, **Activation**, **Re-engagement**. Bruk **entry triggers** på events, **holdouts** for kausal effekt, **subscription groups** for SMS/e-post-samtykke.

  ## **Iterable (E)**

* **Kjerne:** Journey Builder, event-/profil-/katalog-data, kanaler (e-post/SMS/push/in-app), data feeds, eksperimenter.

* **Best på:** Datadrevet personalisering når du har rikt bruker-/produktdata.

* **Hvorfor/hvordan:** Modellér **user events** (signup, view, cart, purchase), legg produktfeeds i **Catalogs**, bygg journeys med **filters/branches**, og kjør **experiments** pr. node for løpende vinner-valg.

  ## **ActiveCampaign (SMB)**

* **Kjerne:** Automations (if/else, goals, waits), e-post, lett CRM/deals, lead score, site & event tracking.

* **Best på:** SMB leadgen \+ e-postnurture uten tung kompleksitet.

* **Hvorfor/hvordan:** Lag 4 “recipes”: **Lead magnet → Nurture**, **New lead → SDR alert**, **Abandoned cart/browse**, **Post-purchase upsell**. Bruk **tags** som enkel “state machine” og **Goals** for å hoppe i flows.

  ## **Klaviyo (e-handel)**

* **Kjerne:** Dyp Shopify/Woo/BigCommerce-integrasjon, prediktive målinger (CLV/Churn), segmenter, dynamiske produktblokker, SMS.

* **Best på:** E-handel: abandoned cart/browse, win-back, post-purchase, back-in-stock.

* **Hvorfor/hvordan:** Aktiver standard-flows (Welcome, **Abandoned Cart**, **Browse Abandon**, **Post-Purchase**), bruk **Viewed Product** \+ **Added to Cart** som triggere, **price-drop/back-in-stock** varsler, og test **predictive splits** for CLV-styrt kommunikasjon.

  ## **Mailchimp (SMB)**

* **Kjerne:** Audience/Tags/Segments, Customer Journey Builder, kampanjer, grunnleggende e-handelssync, maler, enkle rapporter.

* **Best på:** Enkelt nyhetsbrev/lett journey for små lister/sideprosjekter.

* **Hvorfor/hvordan:** Hold **én audience**, segmentér med **tags**, bygg 2–3 journeys (Welcome, Re-engage, Post-purchase), og bruk **A/B** på emne/innhold før du skalerer.

  ## **Brevo / Sendinblue (SMB/EU)**

* **Kjerne:** E-post/SMS/WhatsApp, transaksjonell SMTP, automation, grunn-CRM, prisgunstig, EU/GDPR-vennlig.

* **Best på:** SMB i EU som vil kombinere markedsføring \+ transaksjonell utsending.

* **Hvorfor/hvordan:** Skill **marketing** vs. **transactional** (egen IP/domene om mulig), lag **double opt-in** skjema, bygg **RFM-segmenter** for kampanjer, og bruk **SMS** for tidssensitive påminnelser.

  ## **Mautic (OS)**

* **Kjerne:** Open-source kampanjer/segmenter, dynamisk innhold, forms, kanaler (e-post/SMS), plugins, selvhost.

* **Best på:** Full kontroll/on-prem og lav lisenskost ved teknisk kapasitet.

* **Hvorfor/hvordan:** Sett opp **cron-jobs** (segments:update, campaigns:trigger), bruk **Themes**/**Custom Fields**, og legg integrasjoner via webhook/REST. Planlegg **oppgraderinger** og sikkerhet aktivt.

  ## **Mixpanel (analyse)**

* **Kjerne:** Eventer/props, funnels, kohorter, retention, Paths/Journeys, Group Analytics, impact-analyse.

* **Best på:** Produkt/growth-innsikt som styrer *hvilke* journeys du bør sende.

* **Hvorfor/hvordan:** Definér **north-star** og kritiske events (view → add to cart → purchase), bygg **kohorter** (f.eks. ikke aktiv 7 dager) og **sync** dem til MA-verktøy (via Reverse ETL) for målrettede kampanjer.

  ---

  ## **Hvem passer med hvem? (vanlige stacks)**

* **Enterprise B2B:** Marketo \+ Salesforce \+ Chili Piper \+ Clari (+ Mixpanel/GA4 for produkt/web).

* **Produkt-/app-fokus:** Braze **eller** Iterable \+ Segment/dbt \+ Mixpanel.

* **SMB leadgen:** ActiveCampaign \+ Pipedrive/HubSpot Starter \+ Make \+ Cal.com.

* **E-handel:** Klaviyo \+ Shopify \+ Meta CAPI \+ Mixpanel (eller GA4) \+ Reviews-app.

* **EU budsjett:** Brevo \+ Woo/Shopify \+ Make \+ Cal.com (SMS/WhatsApp ved behov).

* **Selvhost/kontroll:** Mautic \+ Postfix/SMTP \+ n8n \+ Matomo/Mixpanel.

---

# 

# **Meldinger, DM-bots, Chat & Kundestøtte**

## **Intercom**

* **Kjerne:** Live chat, innboks, bots, help center, product tours, e-post/push.

* **Best på:** SaaS/produktdrevne team som vil ha én kundehub.

* **Hvorfor/hvordan:** Bruk **inbox rules** \+ bot for triage, **Product Tours** for onboarding, og koble til CRM for full kontekst.

  ## **Drift**

* **Kjerne:** Conversational marketing, playbooks, chatbot, ABM, instant booking.

* **Best på:** B2B inbound som skal bli møter i kalenderen raskt.

* **Hvorfor/hvordan:** Bygg **playbooks** som kvalifiserer og booker automatisk (gjerne med Chili Piper), ruter på konto/territorium.

  ## **Manychat**

* **Kjerne:** IG/Messenger DM-flows, comment→DM, story mentions, webhooks.

* **Best på:** Vekst via IG Reels/Kommentar→DM \+ lead-capture.

* **Hvorfor/hvordan:** Lag **flows** for kvalifisering/opt-in, følg Meta-regler (samtykke/vinduer), håndover til agent/CRM via webhook.

  ## **Chatfuel**

* **Kjerne:** No-code bot-bygger for IG/Messenger, templates, enkle integrasjoner.

* **Best på:** Raskt i gang med IG/Messenger uten kode.

* **Hvorfor/hvordan:** Start med maler (FAQ, giveaway, lead), koble til Google Sheets/CRM, hold deg innenfor Meta-policy.

  ## **Landbot**

* **Kjerne:** Web- og WhatsApp-chatbots, forms/conditional logic, integrasjoner.

* **Best på:** **WhatsApp-først** opplevelser \+ webchat uten kode.

* **Hvorfor/hvordan:** Bruk **WhatsApp-flows** for kvalifisering, send til live agent ved behov, logg til CRM via webhook/Make.

  ## **Crisp**

* **Kjerne:** Delt innboks (mail/chat/SoMe), kampanjer, bot, kunnskapsbase.

* **Best på:** SMB som vil ha én rimelig kundehub på tvers av domener.

* **Hvorfor/hvordan:** Sett **routing/assign**\-regler, bygg en lett **bot** for FAQ, og bruk kampanjer for segmenterte utsendelser.

  ## **Tidio**

* **Kjerne:** Chat-widget, AI-bot (forenklet), e-handelstriggere (Shopify/Woo), automasjoner.

* **Best på:** Nettbutikker som vil øke konvertering og redde handlekurver.

* **Hvorfor/hvordan:** Aktiver **cart/browse-triggere**, lag bot for vanlige spørsmål, mål “chat→checkout”.

  ## **Front**

* **Kjerne:** Omnikanal **delt innboks** (e-post/SMS/SoMe), regler, SLA, interne kommentarer.

* **Best på:** Team som lever i e-post men må samarbeide strukturt.

* **Hvorfor/hvordan:** Bruk **rules/SLAs** per kanal, del **drafts** internt, koble til CRM for auto-oppslag og logging.

  ## **Zendesk**

* **Kjerne:** Tickets, omnikanal, help center, macros, SLAs, Sunshine (plattform).

* **Best på:** Moden helpdesk med stort økosystem/integrasjoner.

* **Hvorfor/hvordan:** Standardiser **ticket forms/fields**, bruk **macros/triggers** for konsistens, bygg knowledge base → avlast chat.

  ## **Freshdesk**

* **Kjerne:** Tickets, automasjoner, SLAs, bots, kunnskapsbase (Freshworks-suite).

* **Best på:** Budsjettvennlig, “Zendesk-light” med god dekning.

* **Hvorfor/hvordan:** Sett **priority/SLA**\-policy, bygg scenario-automations, koble **Freshsales** for 360-visning.

  ## **ServiceNow (E)**

* **Kjerne:** ITSM/CSM, workflows, Virtual Agent, Knowledge, tung governance.

* **Best på:** Enterprise service management på tvers av avdelinger.

* **Hvorfor/hvordan:** Modellér prosesser i **Flow Designer**, bruk **CSM** for kundeforespørsler, stram tilgang/CI-katalog.

  ## **Meta Business Suite**

* **Kjerne:** Administrer FB/IG-sider, planlegg innhold, samlet innboks, enkle autosvar.

* **Best på:** Grunnleggende SoMe-publisering \+ svar i én innboks.

* **Hvorfor/hvordan:** Planlegg innlegg/Reels, aktiver **FAQ/autosvar**, synk samtaler til CRM via iPaaS (Make/n8n) når det trengs.

  ---

  ## **Vanlige kombinasjoner**

* **Web/app:** Intercom **eller** Drift (chat/bot) \+ CRM (HubSpot/SFDC) \+ Chili Piper (booking).

* **IG/Messenger:** Manychat **eller** Chatfuel \+ Meta Business Suite (innhold) \+ iPaaS for CRM-logging.

* **WhatsApp-først:** Landbot \+ WhatsApp Business Platform (via BSP) \+ CRM.

* **Kundeservice:** Zendesk **eller** Freshdesk \+ kunnskapsbase \+ Intercom/Front for live chat.

* **E-handel:** Tidio/Crisp \+ Klaviyo/Brevo (e-post/SMS) \+ Shopify/Woo.

---

# **Planlegging, Kalender & Booking**

## **Cal.com (OS)**

* **Kjerne:** Open-source booking, multi-brand/multi-team, round-robin, routing forms, payments, webhooks, self-host eller SaaS.

* **Best på:** Flere brands/ressurser, streng kontroll (self-host), avanserte ruter.

* **Hvorfor/hvordan:** Lag **Event Types** per brand, bruk **Routing Forms** for kvalifisering, sett **buffers**/arbeidstid, og send webhooks til CRM (Make/n8n). Vurder **self-host** for data­kontroll.

  ## **Calendly**

* **Kjerne:** Event types, pooled/round-robin, routing forms, workflows (e-post/SMS), brede integrasjoner.

* **Best på:** “Det bare funker” standard for link-booking i B2B.

* **Hvorfor/hvordan:** Bruk **pooled availability** for team, **routing** (territorium/produkt), og **workflows** for påminnelser/oppfølging. Koble til CRM for auto-oppgaver.

  ## **SavvyCal**

* **Kjerne:** Kalendere-overlay, forslag begge veier, preferanser/priority, team-slots.

* **Best på:** Gjest-vennlig booking (mindre friksjon, høyere oppmøte).

* **Hvorfor/hvordan:** Del lenker der gjesten kan **foreslå tid**; lag **ranked availability** (morgen vs. ettermiddag), og bruk **overlay** av flere kalendere.

  ## **Motion**

* **Kjerne:** AI-planlegger som auto-timeboxer oppgaver \+ flytter møter smart.

* **Best på:** Solo/leder med masse oppgaver/deadlines og lite planleggingstid.

* **Hvorfor/hvordan:** Opprett oppgaver med **estimat/deadline/priority**; la Motion auto-plassere. Lås viktige blokker (no-move) og la resten flyte.

  ## **Reclaim.ai**

* **Kjerne:** Auto-timeboxing for **tasks** og **habits**, smart reschedule, team-policy for møter.

* **Best på:** Balanse mellom vaner (trening/admin) og møter uten å miste fokus.

* **Hvorfor/hvordan:** Definér **Habits** (f.eks. “regnskap man/tor”), legg tasks med SLA; Reclaim flytter dem når kalenderen endres. Synk med Slack for status.

  ## **Clockwise**

* **Kjerne:** Fokus-blokk optimalisering, “smart holds”, team-koordinering, fleksibilitetsvinduer.

* **Best på:** Team/avdelinger som vil redusere møtekollisjoner og øke **fokus-timer**.

* **Hvorfor/hvordan:** Sett **Focus Time goals**, angi hvilke møter kan flyttes (+/- fleksibilitet), og la Clockwise optimalisere tverr-team.

  ## **Sunsama**

* **Kjerne:** Daglig planlegger som samler oppgaver (Asana/ClickUp/Jira/Trello/Email) \+ kalender, manuelt men rolig fokus.

* **Best på:** Personlig “calm productivity” \+ realistisk dagplan.

* **Hvorfor/hvordan:** Morgenrituale: dra oppgaver inn i dagen, **timebox**, og logg faktisk tid. Hold backlog i verktøyet ditt, plan i Sunsama.

  ## **Acuity Scheduling**

* **Kjerne:** Avansert booking, intake-skjema, pakker/abonnementer, kuponger, betalinger (Squarespace).

* **Best på:** Tjenesteytere/klinikker/verksteder med **formularer \+ betaling** før time.

* **Hvorfor/hvordan:** Lag **Appointment Types** m/ buffer, **Intake Forms** (felter), **Packages** for klippekort, og ta betalt ved booking.

  ## **YouCanBook.me**

* **Kjerne:** Enkel booking over Google/Microsoft, custom felter, varsler, ruter.

* **Best på:** Rimelig, rett-fram teambooking uten stor kompleksitet.

* **Hvorfor/hvordan:** Lag **templates** per rolle/brand, bruk **custom questions** for kvalifisering, og send **ICS**/SMS-varsler.

  ## **Cronofy (API)**

* **Kjerne:** Enterprise **scheduling API**, real-time availability over Google/Microsoft/Apple, “Smart Invites”, enterprise-sikkerhet.

* **Best på:** Å bygge **booking inn i egne apper** (B2B/B2C) med granulær kontroll.

* **Hvorfor/hvordan:** Bruk **Enterprise Connect** for dyp kalender-tilkobling, **Availability API** for regler (buffers, arbeidsvinduer), og **Smart Invites** for robust ICS.

  ## **Nylas (API)**

* **Kjerne:** Unified **email/calendar/contacts API**, webhooks, Scheduler-komponent.

* **Best på:** Rask multi-leverandør-integrasjon (Gmail/Outlook/Exchange) i én API.

* **Hvorfor/hvordan:** Autentiser brukeres kontoer, lytt på **webhooks** (ny avtalestatus), og embedd **Nylas Scheduler** for booking. Avklar databehandlings-krav (DPA).

  ## **Google Calendar API**

* **Kjerne:** Direkte API til Google Calendar: events, ACL, free/busy, push-varsler.

* **Best på:** Maksimal kontroll når du **selv** bygger logikken.

* **Hvorfor/hvordan:** Bruk **service accounts/OAuth**, **Channels** (push notifications) for endringer, og bygg regler for **freeBusy** \+ buffers selv. Husk kvoter.

  ---

  ## **Vanlige kombinasjoner**

* **Flere brands \+ CRM:** Cal.com/Calendly \+ HubSpot/Pipedrive \+ Make (webhook → opprett contact/deal, send bekreftelse).

* **AI-plan \+ booking:** Reclaim/Motion for tasks \+ Cal.com for eksterne møter.

* **Klinikk/verksted:** Acuity (skjema+betaling) \+ SMS-påminnelser \+ Google Calendar.

* **Egne produkter/apper:** Cronofy **eller** Nylas \+ eget UI \+ Stripe.

---

# **Integrasjon, iPaaS, RPA & Nettleser-automatisering**

## **Make (EU-vennlig)**

* **Kjerne:** Visuelle scenarier, webhooks, iterator/aggregator, Data Stores, scheduling, mange connectors.

* **Best på:** SMB/agency som vil bygge raske, robuste flows med EU-databehandling.

* **Hvorfor/hvordan:** Start med **Webhook → Transform → Action**\-mønster; bruk **Routers** for grener, **Error handlers** for retry/branch, og **Data Stores** for idempotens/dedupe. God for IG/Messenger→CRM→Kalender.

  ## **Zapier**

* **Kjerne:** Enorm app-dekning, “Zaps” med triggere/handlinger, no-code logikk.

* **Best på:** Kjapp prototyping og standard integrasjoner uten dev-ressurser.

* **Hvorfor/hvordan:** Bruk **Paths/Filters** for enkel branching, **Storage by Zapier** for små states, hold øye med **Task-kost** og rate limits ved skala.

  ## **Workato (Enterprise)**

* **Kjerne:** iPaaS med **Recipes**, RBAC, versjonering, approvals, SDK for connectors.

* **Best på:** Enterprise-governance, sikkerhet og skalerbare integrasjoner.

* **Hvorfor/hvordan:** Bygg **Reusable Recipes** (sub-recipes), bruk **Connections** med secrets-styring, sett **Error policies**/observability for drift.

  ## **Tray.io (Enterprise)**

* **Kjerne:** Low-code visuelle workflows, dype API-steg, skalerbar kjøring.

* **Best på:** Mid-market/enterprise som trenger fleksible API-pipelines.

* **Hvorfor/hvordan:** Modellér **API-orchestration** (pagination, rate limiting), bruk **Callable workflows** for gjenbruk, og konfigurer **Workspace-governance**.

  ## **n8n (Open-source)**

* **Kjerne:** Selvhostbar iPaaS, nodes \+ **Function/Code** noder (JS), credentials-vault.

* **Best på:** Kontroll/privatliv (on-prem), kombinasjon av no-code \+ kode.

* **Hvorfor/hvordan:** Kjør i Docker; bygg **trigger → nodes → code**; lag **Queues** (BullMQ/Redis) for tunge tasks; fint sammen med Mautic/Matomo.

  ## **Microsoft Power Automate**

* **Kjerne:** 1000+ connectors, dyp M365/Dataverse/SharePoint, **Desktop flows (RPA)**.

* **Best på:** Bedrifter på Microsoft-stacken (Teams/Outlook/SharePoint).

* **Hvorfor/hvordan:** Bruk **Cloud flows** for API-integrasjon og **Desktop flows** for UI-RPA; kombinér med **Power Apps** og **Power BI**.

  ## **Pipedream**

* **Kjerne:** Kode-først serverless workflows (Node/Python), raske webhooks, npm-økosystem.

* **Best på:** Dev-team som vil lime API-er sammen med litt kode.

* **Hvorfor/hvordan:** Skriv små **steps** i JS/Py, bruk **sources** for events, **$checkpoint** for state, og utnytt npm-pakker direkte.

  ## **Node-RED (Open-source)**

* **Kjerne:** Visuelle flows, MQTT/IoT, HTTP-nodes, kan kjøre på Raspberry Pi.

* **Best på:** IoT/edge og enkle API-broer i eget miljø.

* **Hvorfor/hvordan:** Bygg **dashboard** raskt, koble sensorer via **MQTT**, eksponer **HTTP In/Out** som minitjenester.

  ## **IFTTT**

* **Kjerne:** Enkle “If This Then That”-oppskrifter, forbruker-/SoMe-fokus.

* **Best på:** Lett automasjon for enkle oppgaver; ikke for proff drift.

* **Hvorfor/hvordan:** Bruk til personlige varsler/enkle triggere, unngå kritiske forretningsprosesser.

  ## **UiPath (Enterprise RPA)**

* **Kjerne:** Attended/unattended bots, **Studio**, **Orchestrator**, dokument-AI.

* **Best på:** Automatisere legacy GUI/desktop, ERP/finansprosesser i skala.

* **Hvorfor/hvordan:** Identifiser høyt volum, regelbaserte prosesser; bygg **robuste selektorer**, bruk **Queues**/**REFramework**, overvåk i **Orchestrator**.

  ## **Automation Anywhere (Enterprise RPA)**

* **Kjerne:** Cloud-native RPA, **Bot Insight**, IQ Bot (dokumenter).

* **Best på:** Enterprise RPA med sky-drift og innebygd analyse.

* **Hvorfor/hvordan:** Standardiser **Bot-livssyklus** (dev/test/prod), bruk **IQ Bot** for faktura/PO/innboks-dokumenter.

  ## **Bardeen**

* **Kjerne:** Nettleser-automatisering, “playbooks”, UI-skraping (DOM), manuell+auto.

* **Best på:** Personlig/SMB automatisering direkte i nettleseren (CRM-berikelse, scraping).

* **Hvorfor/hvordan:** Lag playbooks som **leser DOM → skriver til tabell/CRM**; vær obs på **ToS** og sprø API-grenser/sperrer ved scraping.

  ## **Zoho Flow**

* **Kjerne:** iPaaS i Zoho-økosystemet, connectors, enkel logikk.

* **Best på:** Team som kjører **Zoho CRM/Books/Desk** og vil holde seg “in-suite”.

* **Hvorfor/hvordan:** Koble Zoho-apper først; bruk **webhooks** for 3.parts; sentraliser feilvarsler.

  ## **Parabola**

* **Kjerne:** No-code dataflows/ETL, CSV/Shopify/HubSpot, planer og filtre/joins.

* **Best på:** E-handel/ops som må rydde og synke data uten kode.

* **Hvorfor/hvordan:** Lag **import → clean → join → export**\-flows; planlegg kjøring (hourly/daily); bruk for feed-berikelse (Klaviyo/Ads/CRM).

  ---

  ## **Vanlige kombinasjoner**

* **SMB/Agency (EU):** Make \+ HubSpot/Pipedrive \+ Manychat/Meta \+ Cal.com.

* **Dev-tyngde:** Pipedream \+ GitHub \+ Slack \+ egen Postgres/S3.

* **MS-hus:** Power Automate \+ SharePoint/Dataverse \+ Power BI.

* **Self-host & kontroll:** n8n \+ Mautic \+ Matomo \+ egen SMTP.

* **RPA \+ ERP:** UiPath/Automation Anywhere \+ SAP/Oracle \+ dokument-AI.

* **IoT/Edge:** Node-RED \+ MQTT \+ lokale API-er.

* **E-handel dataops:** Parabola \+ Shopify \+ Klaviyo \+ GA4/Mixpanel.

---

# **SoMe & Annonse-APIer / Styring**

## **Facebook/Meta Graph API**

* **Kjerne:** Tilgang til FB-/IG-ressurser (sider, innlegg, kommentarer, innsikt), webhooks, moderasjon.

* **Best på:** Bygge egne verktøy for publisering, kommentarmoderasjon og innsikt.

* **Hvorfor/hvordan:** Bruk **app-tokens \+ Page/IG-tokens** (med fornyelse), **Webhooks** for hendelser (kommentar/mention), og cache svar for å spare rater. Avklar tillatelser i **App Review** tidlig.

  ## **Instagram Graph API**

* **Kjerne:** IG Business/Creator publisering (feed/reels), innsikt, mentions, kommentarer, webhooks.

* **Best på:** Programmatisk IG-flyt (publiser, svar, mål).

* **Hvorfor/hvordan:** Koble IG Business ↔ FB-side, bruk **Publishing \+ Mentions \+ Insights** endepunkter, og logg feilkoder/ratelimits. Webhooks for **comments/mentions** → CRM.

  ## **Messenger Platform**

* **Kjerne:** DM-bots, quick replies, menyer, **Handover Protocol** (bot ↔ agent), webhooks.

* **Best på:** Inbound DM-kvalifisering \+ overlevering til menneske/CRM.

* **Hvorfor/hvordan:** Følg **24-timers-regelen** for promotering; bruk **One-Time Notification**/message tags der det er lov; håndter **handover** til agent-inboks eller Intercom/Front.

  ## **WhatsApp Business Platform**

* **Kjerne:** Offisiell API (Cloud/API via BSP), mal-meldinger (HSM), toveis dialog, samtale-prising.

* **Best på:** Høy leveranse, kritiske varsler og dialog i global kanal.

* **Hvorfor/hvordan:** Skaff **opt-in**, bygg **template-bibliotek** (marketing/utility/auth), sett opp **conversation-tracking**, og rute til CRM. Husk at **initierte samtaler** prises per kategori/land.

  ## **Facebook Marketing API**

* **Kjerne:** Kampanje/adset/ad, budsjetter, A/B, målgrupper (custom/lookalike), rapporter.

* **Best på:** Programmatisk styring av annonser i skala (budsjett, kreativer, regler).

* **Hvorfor/hvordan:** Modellér **idempotente deploys** (eksterne IDs), bruk **batch** og **async insights**, og bygg **naming-konvensjoner** (Kampanje-mål/land/språk).

  ## **Meta Conversions API (CAPI)**

* **Kjerne:** Server-side events (PageView/Lead/Purchase/Schedule), deduplisering.

* **Best på:** Stabil sporing når cookies/blokkere skaper hull.

* **Hvorfor/hvordan:** Send **event\_id** \+ **fbp/fbc** for dedupe, mapp **content\_ids/value/currency** korrekt, og bygg **retry \+ queue** (Make/n8n/server). Hold **Consent Mode**/samtykke som gate.

  ## **TikTok Marketing API**

* **Kjerne:** Kampanjer/ad groups/ads, katalog, **Events API** (server-side), rapporter.

* **Best på:** Skalerbar TT-annonsering (inkl. katalog/collections).

* **Hvorfor/hvordan:** Koble **Pixel \+ Events API** (dedupe), bruk **creative automation** og **spark ads** (på organiske poster), mål **view→click→purchase** med post-view-vinduer.

  ## **Buffer**

* **Kjerne:** Planlegging/publisering for flere plattformer, enkel kalender/queues, grunn-rapporter.

* **Best på:** Lett redaksjonell kalender for SMB/solo.

* **Hvorfor/hvordan:** Sett **UTM-standard**, bruk **queue-slots** per kanal, kjør reposter på evergreen og se på **best time to post**.

  ## **Hootsuite**

* **Kjerne:** Team-publisering, “listening”, innboks, approvals, rapporter.

* **Best på:** Byråer/markedsavdelinger med governance og volum.

* **Hvorfor/hvordan:** Lag **approval-workflows**, **streams** (søk/mention/hashtags), og dashboard pr. brand/land. Eksporter **krysskanal-rapporter**.

  ## **Sprout Social**

* **Kjerne:** Smart Inbox (omnikanal), tagging, avansert analyse, “listening”.

* **Best på:** Innsikt og kundedialog i team—sterk rapportering.

* **Hvorfor/hvordan:** Standardiser **tag taxonomy** (kampanje/intent), bruk **saved replies**, og bygg **business reviews** dashboards.

  ## **Phantombuster**

* **Kjerne:** Growth/automatisering (prospekter, scraping, SoMe-actions).

* **Best på:** Eksperimentell lead-innhenting der APIer ikke finnes.

* **Hvorfor/hvordan:** Throttle hardt, roter cookies/proxy der lovlig, respekter **ToS/personvern**. Bruk kun hvor **offisielle APIer** ikke dekker behov.

  ---

  ## **Vanlige kombinasjoner**

* **IG/Messenger DM-vekst:** Instagram Graph \+ Messenger Platform \+ Manychat/Chatfuel (flow) \+ **CAPI** (server-side events) \+ CRM (HubSpot/Pipedrive).

* **E-handel:** Facebook Marketing API \+ CAPI \+ Klaviyo \+ Produktkatalog → **ASC (Advantage+ Shopping)**\-styring via API.

* **App/produkt:** Braze/Iterable (journeys) \+ Graph API webhooks (events) \+ CAPI \+ Mixpanel-kohorter.

* **Byrå/innhold:** Hootsuite/Sprout/Buffer for plan/approval \+ Graph API for spesialfunksjoner \+ Marketing API for regler/budsjett.

---

# **Datastack: CDP, ELT, Reverse ETL & Analyse**

## **Segment (CDP)**

* **Kjerne:** Samle inn hendelser (web/app/server), **Sources → Destinations**, identitet (userId/anonymousId), **Schemas/Protocols**, og datastyring.

* **Best på:** Én sann datakilde for kunde-/produktdata som mates til alt annet (MA, analyse, annonser, lager).

* **Hvorfor/hvordan:** Lag en **tracking plan** (events \+ properties), send både **client-** og **server-side** events, bruk **Protocols** til å håndheve skjema (blokker ukjent data), og speil alt til datalager (Snowflake/BigQuery/Redshift). Bruk **Group** for B2B (konto-ID).

  ## **Fivetran (ELT)**

* **Kjerne:** Fullt styrte connectors (SaaS→lager), skjema-drift, inkrementelle laster, CDC på utvalgte kilder.

* **Best på:** Stabil, vedlikeholdsfri innlasting fra tredjepart (Meta Ads, Shopify, HubSpot osv.) til datalager.

* **Hvorfor/hvordan:** Velg **lager** (Snowflake/BigQuery/Redshift), sett **historikk-/sync-vinduer**, overvåk **row-basert** kost, og hold transformasjoner i **dbt** (ikke i kilden).

  ## **dbt (Transform)**

* **Kjerne:** SQL-modeller, **materializations** (view/table/incremental), **tests** (unique/not null/relasjoner), **snapshots** (SCD), **docs** og gjenbruk (Jinja/macros).

* **Best på:** Versjonert, team-vennlig modellering av **staging → marts** (dim/fct) med kvalitetssikring.

* **Hvorfor/hvordan:** Strukturér som `stg_*` (ren kildedata), `int_*` (mellom), `dim_*` og `fct_*`. Legg på **tests** og **snapshots** for SCD. Dokumentér alt og publiser **dbt docs**.

  ## **Hightouch (Reverse ETL)**

* **Kjerne:** Synk fra lager → CRM/MA/annonser (HubSpot, Salesforce, Klaviyo, Meta, Google, TikTok), **audiences**, event-streams.

* **Best på:** Aktivere lagerdata i verktøyene du bruker uten egen lim-kode.

* **Hvorfor/hvordan:** Pek en modell (SQL/dbt) med **primærnøkkel**, mapp felter til destinasjon, velg sync-modus (upsert/patch), og bruk **hashing** for PII til annonseplattformer. La lageret være **source of truth**.

  ## **Mixpanel (Produktanalyse)**

* **Kjerne:** Eventer/props, **funnels**, **retention**, **cohorts**, **Group Analytics**, Paths/Journeys.

* **Best på:** Hurtig produkt-/growth-innsikt som styrer hvilke journeys/kanaler du skal trigge.

* **Hvorfor/hvordan:** Definér **kjerne-events** (view/add\_to\_cart/purchase/booking\_submitted), standardiser **userId** og **groupId** (B2B). Bygg **cohorts** og eksporter dem til MA/annonse via Hightouch.

  ## **Clearbit (Berikelse)**

* **Kjerne:** Firmografisk berikelse (bransje, størrelse, teknologi), **Reveal** (IP→firma), Forms.

* **Best på:** B2B-segmentering/ruting, ABM, kortere skjema (mindre felter).

* **Hvorfor/hvordan:** Kjør **batch/API-berikelse** på lead/konto, bruk **Reveal** på web for å tilpasse innhold. Vær streng på GDPR—bruk legitime kilder og formål.

  ## **ZoomInfo (Data)**

* **Kjerne:** B2B-database, kontaktdata, intensjons-signaler, “Scoops”.

* **Best på:** Prospektering/ABM når du trenger bred B2B-dekning.

* **Hvorfor/hvordan:** Synk til CRM med klare **felter** (kilde, kvalitet), bruk **intent-tema** til prioritering. Husk etterlevelse/GDPR i EU.

  ## **Parabola (no-code ETL)**

* **Kjerne:** Import→transform→export flows (CSV/Shopify/HubSpot), joins/filtre, planlagt kjøring.

* **Best på:** SMB/e-handel som vil rense/forme data uten å kode.

* **Hvorfor/hvordan:** Bygg **feed-flows** (produkt/ordre/kunde), normaliser felter, eksporter til Klaviyo/CRM/Ads. Bra som “ops-verktøy” ved siden av Fivetran/dbt.

  ---

  ## **Vanlige kombinasjoner (arketyper)**

* **Produkt/app (sanntid \+ aktivering)**

  * **Segment** (events) → **Fivetran** (SaaS-kilder) → **BigQuery/Snowflake**

  * **dbt** (stg→dim/fct) → **Mixpanel** (innsikt)

  * **Hightouch** (cohorts/audiences → HubSpot/Meta/TikTok)

* **E-handel (Shopify)**

  * **Fivetran** (Shopify/Ads) → lager → **dbt** (RFM/CLV)

  * **Klaviyo** får lister via **Hightouch**; **Mixpanel** for funnels/retensjon

* **B2B/ABM**

  * **Segment** (+ web events) \+ **Clearbit/ZoomInfo** (berikelse)

  * **Fivetran** (HubSpot/SFDC/Ads) → lager → **dbt**

  * **Hightouch** (målgrupper til Sales/MA/Ads) \+ **Mixpanel** på produktbruk

  ---

  ## **Rask valgsguide**

* **CDP (samle/dirigere events):** Segment

* **ELT (SaaS→lager, minst vedlikehold):** Fivetran

* **Transform (modeller/testing/dokumentasjon):** dbt

* **Aktivering (lager→verktøy/annonser):** Hightouch

* **Produktinnsikt:** Mixpanel

* **B2B-berikelse:** Clearbit (lett) / ZoomInfo (tung dekning)

* **SMB no-code ETL:** Parabola

---

# 

# **AI-rammeverk, kodeassistenter & plattformer**

## **Google Vertex AI**

* **Kjerne:** Managed tren/hosting av modeller (LLM/klassisk ML), endpoints for sanntid/batch, pipelines, vektor-/RAG-komponenter, datastyring og MLOps på GCP.

* **Best på:** Produksjonsklar ML/LLM i Google-skyen med skalerbarhet, sikkerhet og governance.

* **Hvorfor/hvordan:** Bygg **Pipelines** for tren/deploy, servér via **Endpoints**, bruk **vector search** \+ dokumentkilder for RAG, og styr secrets/tilganger via IAM. God når du vil ha “one-stop” plattform \+ compliance.

  ## **LangChain**

* **Kjerne:** Komponenter for **chains**, **agents**, verktøy/funksjonskall, minne, retrievers; stort integrasjonsøkosystem.

* **Best på:** Raskt å bygge LLM-apper/arbeidsflyter (tool-use, samtale-trinn, beslutningslogikk).

* **Hvorfor/hvordan:** Modellér flyt som **chain/agent**, koble **tools** (søk, DB, API), bruk **retriever** for kunnskap, og test med eval/trace. Start enkelt (prompt → tool) før multi-step.

  ## **LlamaIndex**

* **Kjerne:** RAG-fokus: datainntak/connectors, chunking/“nodes”, indekser (vektor/tre/keyword), **retrievers**, query-engine, evaluering/observability.

* **Best på:** Nøyaktig RAG over egne dokumenter/data uten mye lim-kode.

* **Hvorfor/hvordan:** Bygg **ingestion pipeline** (parser → chunk → lagring), velg **index \+ retriever** (vektor \+ rerank), slå på **eval** (groundedness/latency), og cache resultater. Fungerer utmerket sammen med LangChain/Vertex.

  ## 

  ## **AutoGen**

* **Kjerne:** **Multi-agent** orkestrering (AI↔AI og AI↔menneske), rolle-agenter (Planner/Coder/Critic), verktøy-kall og gruppesamtaler.

* **Best på:** Komplekse oppgaver som krever samarbeid (kodegenerering, research, flerstegs-automatisering) med menneskelig godkjenning.

* **Hvorfor/hvordan:** Definér 2–4 spesialiserte agenter, registrér **tools**/APIer, sett **stoppkriterier**/timeouts for å unngå løkker, og logg samtaler for revisjon. Start med *Planner \+ Executor \+ Reviewer*.

  ## **GitHub Copilot**

* **Kjerne:** Kodefullføringer i IDE, chat/forklaring, test-/snutt-generering, PR-hjelp.

* **Best på:** Fart i hverdagskoding, boilerplate, tests, ukjent API-bruk—rett i VS Code/JetBrains.

* **Hvorfor/hvordan:** Skriv målrettede **kommentarer/Docstrings** for kontekst, bruk **Copilot Chat** for refaktor/forklaring, valider med linters/tester, og behold “human-in-the-loop”.

  ---

  ## **Vanlige kombinasjoner**

* **RAG-app raskt:** *LlamaIndex (ingest+retrieval) \+ LangChain (agent/flow) \+ Vertex AI (hosting/endpoints)*.

* **Komplekse oppgaver:** *AutoGen (flere agenter) \+ LangChain-tools*; menneske godkjenner kritiske steg.

* **Dev-hverdagen:** *Copilot* for koding \+ *LangChain/LlamaIndex* for app-logikk \+ *Vertex* for prod.

---

# 

# **Produktivitet, Work-OS & Interne verktøy**

## **ClickUp**

* **Kjerne:** Prosjekter/oppgaver, mål, tidslinjer, dashboards, automasjoner, docs.

* **Best på:** Én hub for prosjekter \+ operasjonelle prosesser med mye granularitet.

* **Hvorfor/hvordan:** Lag **Spaces → Folders → Lists**, definer **Custom Fields**, sett **Automations** (status→oppgave→varsel), og bygg **dashboards** for KPI.

  ## **Monday.com**

* **Kjerne:** Boards/visninger, automatiseringer, integrasjoner, lett CRM, WorkForms.

* **Best på:** Tverrteam-prosesser og “no-code” flows som er lette å adoptere.

* **Hvorfor/hvordan:** Modellér hver prosess som et **board** med **status/people/date**\-kolonner; bruk **Automations** (if/then) og **Integrations** (Slack/HubSpot).

  ## **Notion \+ Notion AI**

* **Kjerne:** Wiki, databaser, relasjoner/rullups, page-templates, AI-skriving/spørring.

* **Best på:** Kunnskap \+ lett CRM/ops i samme fleksible verktøy.

* **Hvorfor/hvordan:** Bygg **database-relasjoner** (Prosjekter ↔ Tasks ↔ Docs), lag **templates** (SOP, møtenotater), og bruk **AI** til oppsummering/uttrekk.

  ## **Airtable**

* **Kjerne:** Database-regneark, **Automations**, Interfaces (app-UI), god API/webhooks.

* **Best på:** Operativ “lett-DB” som snakker fint med CRM/marketing via iPaaS.

* **Hvorfor/hvordan:** Normaliser tabeller (Leads, Produkter, Bestillinger), lag **Automations** (record change → e-post/webhook), og bygg **Interfaces** for teamet.

  ## **Asana (+ Intelligence)**

* **Kjerne:** Prosjekter/roadmaps, workload, regler/automations, forms, AI-assist.

* **Best på:** Strukturert prosjektleveranse med avhengigheter og rapportering.

* **Hvorfor/hvordan:** Bruk **Portfolios** og **Goals**, sett **Rules** (status→assignee), og la **Asana Intelligence** foreslå trinn/forfallsdatoer.

  ## **Coda \+ Coda AI**

* **Kjerne:** Docs \+ tabeller med **Buttons**, **Automations**, Packs (integrasjoner).

* **Best på:** Skreddersy “mini-apper” i dokumenter med logikk og API-kall.

* **Hvorfor/hvordan:** Lag **Packs**\-koblinger (HubSpot/Slack), bygg **Buttons** som kjører flows, og bruk **AI** for tekst/ops-forslag.

  ## **Retool**

* **Kjerne:** Drag-and-drop interne apper, koble databaser/APIer, queries, RBAC.

* **Best på:** Raskt bygge admin-/operasjons-UI over dine data (Postgres, REST).

* **Hvorfor/hvordan:** Definér **resources** (DB/API), skriv **queries** (SQL/JS), bind til komponenter (tabeller/forms), legg **actions** (approve/deny).

  ## **Pipefy**

* **Kjerne:** Prosess/kanban-rør (Pipes), skjema, SLA/automations, dokumentgenerering.

* **Best på:** Gjentakende forretningsprosesser (innkjøp, HR, service) uten koding.

* **Hvorfor/hvordan:** Modellér hvert trinn som en **fase** med obligatoriske felter; bruk **Automations** for ruting/SLA; eksporter data til BI.

  ## 

  ## **Slack (Workflow & Events API)**

* **Kjerne:** Kanaler/DM, Workflow Builder, bots/apps, Events/Webhooks, modals.

* **Best på:** Operativ nerve – varsler, godkjenninger, “human-in-the-loop”.

* **Hvorfor/hvordan:** Bygg **Workflows** (form→action), koble iPaaS for **CRM-varsler**, og bruk **slash-commands** for raske handlinger (f.eks. /book, /status).

  ## **Superhuman**

* **Kjerne:** Lynrask e-postklient, AI-svar/triage, oppfølging/påminnelser.

* **Best på:** Individuell produktivitet for tung e-postbruk i salg/ledelse.

* **Hvorfor/hvordan:** Sett **snippets** og **follow-up**\-regler; bruk **AI triage** for prioritert inbox; hold “inbox zero” ritual.

  ## **AppSheet (Google)**

* **Kjerne:** No-code apper fra Sheets/SQL, regler, offline, kamera/GPS.

* **Best på:** Felt-/skjema-apper (inspeksjon, ordre, lager) uten kode.

* **Hvorfor/hvordan:** Knytt til **Sheets/BigQuery**, bygg visninger (Detail/Form/Deck), legg **behaviors** (submit→e-post/webhook), og publiser til mobil.

  ## **Google Apps Script**

* **Kjerne:** JS-skript for Gmail/Sheets/Drive/Calendar, tidsstyrte triggere, web-apps.

* **Best på:** Små “lim-skript” og automasjoner direkte i Google Workspace.

* **Hvorfor/hvordan:** Lag **time-driven triggers** (daglig sync), bygg **web app** (doGet/doPost) som webhook-endepunkt, og kall eksterne API-er.

  ---

  ## **Vanlige kombinasjoner**

* **Kunnskap \+ oppgaver:** Notion (wiki/DB) \+ ClickUp/Asana for leveranse.

* **Operativ DB \+ CRM-lim:** Airtable \+ Make → HubSpot/Pipedrive.

* **Interne apper:** Retool over Postgres/Sheets \+ Slack-varsler.

* **Prosesser uten kode:** Monday/Pipefy \+ iPaaS (Make) for eksterne koblinger.

* **Google-hus:** Apps Script \+ AppSheet \+ Calendar/Drive.

  ## **Rask valgsguide**

* **Prosjektstyring “alt-i-ett”:** ClickUp / Asana

* **Prosess/boards \+ lett CRM:** Monday.com

* **Wiki \+ fleksibel databank:** Notion (AI for tekst/QA)

* **Operativ lett-DB & API-vennlig:** Airtable

* **Interne verktøy raskt:** Retool

* **Formalisert prosessmotor:** Pipefy

* **Operativ kommunikasjon:** Slack (workflows/bots)

* **Personlig e-post-fart:** Superhuman

* **Google-first no-code:** AppSheet

* **Google-lim/skript:** Apps Script

  ## **Mini-oppsett for deg (konkret)**

* **Butikk/verksted:** Airtable (Jobbkort) ↔ ClickUp (oppgaver) → Slack-varsler; AppSheet for innsjekk/foto i verksted.

* **Villa Maleyna:** Notion (SOP/husregler) \+ Airtable (bookinger/oppgaver) → Make → Cal.com & Slack.

* **Etsy/produkt:** Airtable (SKU/innhold) → Notion (briefs) → ClickUp (foto/listing) \+ Slack godkjenning.

* **Dev/Trading:** Retool (admin-UI over DB/logg) \+ Slack / Apps Script for små sync-jobber.

---

# **Nettsted, Funnels & Konvertering**

# **ClickFunnels**

* **Kjerne:** Drag-and-drop landingssider, funnels (opt-in → sales → checkout), order bumps, **upsell/downsell (OTO)**, medlemsområde, A/B-testing, analytics, integrasjoner (Stripe/PayPal, webhooks, Zapier).

* **Best på:** Direct-response salg og skalering av **gjennomsnittlig ordreverdi** via bumps \+ OTO-er (kurs, info-produkter, høymargin fysiske varer).

* **Hvorfor/hvordan (hurtigoppskrift):**

  1. **Struktur:** Opt-in → Sales → Checkout → OTO1 (premium) → Downsells.

  2. **AOV-løft:** 1 order bump (lite tillegg, 9–19% attach); 1–2 OTOer.

  3. **Sporing:** Eget domene \+ **UTM-naming**, GA4, Meta-piksel \+ **CAPI** (via server/iPaaS).

  4. **Fart:** Mobil-først; komprimer bilder; fold-over-fold copy med sosial bevis.

  5. **Drift:** Split-test **overskrift** først, deretter pris/tilbud. Kill tapere raskt.

  # **Systeme.io**

* **Kjerne:** Alt-i-ett på budsjett: nettsider/funnels, e-post (broadcast \+ automations), tags/seg­menter, enkle work­flows, kurs/medlemskap, affiliate-program, checkout (Stripe/PayPal).

* **Best på:** Rask utrulling for **solo/SMB/affiliates** som vil ha **funnel \+ e-post** uten ekstra verktøy.

* **Hvorfor/hvordan (hurtigoppskrift):**

  1. **Domene & e-post:** Sett DMARC/SPF/DKIM; 1 liste, **tags** for atferd (opt-in, kjøp, avbrutt).

  2. **Flows:** Welcome (3–5 e-poster), Abandon (2–3), Post-purchase (3).

  3. **Checkout:** Stripe; enkel **order bump**; kvittering \+ automasjon på **purchase**.

  4. **Oppfølging:** Automations: *If tag=opt-in & no purchase 72t → tilbud*.

  5. **A/B:** Test hero-overskrift og CTA-tekst først.

  ---

  ## **Rask valgsguide**

* **Maks AOV/upsell-kraft \+ moden økosystem:** **ClickFunnels**

* **Billigst alt-i-ett med innebygd e-post & kurs/affiliate:** **Systeme.io**

* **Allerede sterk e-post (Klaviyo/Brevo):** Bruk **ClickFunnels** som landings-/checkout-lag, la e-post bo i e-post-plattformen.

---

# Her er en minimal, “proff” stack skreddersydd til deg (Norge/EU, flere brands, Meta/IG/Messenger, nettverkssalg, service-booking, Etsy):

# **A) Velg retning**

**Option 1 – Alt-i-ett (raskest å drifte):**

* **GoHighLevel (GHL)** – CRM, funnels, SMS/WhatsApp (via Twilio), kalender, workflows

* **Manychat** – IG/Messenger-DM, lead capture \+ handover til GHL

* **Cal.com** – booking (multi-kalender, ruter riktig brand/ressurs)

* **Make** – limet mellom alt (EU-vennlig)

* **Meta Conversions API** – server-side events for presis sporing

* **Brevo** (eller **Klaviyo** for e-com) – e-post/SMS flows (GDPR-vennlig)

* **Airtable** – lett datalager/operativ hub (prospekter, inventar, kampanjer)

* **Mixpanel** – produkt-/growth-analyse på tvers av brands

* **Slack** – operativ varslingskanal (MQL/SQL, no-show, VIP)

* **LangChain \+ LlamaIndex** (+ valgfri LLM) – egen AI-agent for playbooks/SOP/QA

**Option 2 – Komponerbar (mer fleksibel, dev-vennlig):**

* **HubSpot Pro** (CRM, Sales, Marketing)

* **Cal.com** \+ **Reclaim.ai** (planlegger \+ booking)

* **Manychat** \+ **Messenger/IG Graph API** (DM-flows \+ webhooker)

* **Make**/**n8n**/**Pipedream** (integrasjoner/API)

* **Airtable**/**Notion** (operativ database \+ dokumentasjon)

* **Brevo/Klaviyo** (e-post/SMS)

* **Meta CAPI** \+ **GA4** \+ **Mixpanel** (måling)

* **Stripe** (betalingslenker for deposits, reparasjoner, bookinger)

* **S3/Cloudflare R2** (filopplasting av kvitteringer, kontrakter)

* **LangChain \+ AutoGen** (interne AI-agenter for lead scoring/oppfølging)

# **B) 5 “Day-1” automasjoner (plug-and-play)**

1. **IG/Messenger → CRM \+ booking:**  
    DM-trigger (Manychat) → kvalifiseringsspørsmål → webhook → Make → opprett kontakt \+ pipeline-stage i CRM → send **Cal.com**\-lenke → logg samtale → Slack-varsel.

2. **Lead score \+ oppfølging:**  
    Når lead får score ≥ X → auto-oppgave til deg \+ SMS/e-post mal → hvis ikke booket innen 24 t → ny DM/e-post \+ flytt stage.

3. **Meta CAPI robust sporing:**  
    Skjemasend/DM-mål → Make server-side event → Meta CAPI (PageView/Lead/Schedule) \+ dedup med fbp/fbc → bedre ROAS.

4. **Service/repair pipeline (butikken):**  
    Webskjema → CRM “Intake” → opprett jobbkort (Airtable) → Slack til verksted → SMS til kunde (Brevo) ved statusendring.

5. **Villa/booking (villamaleyna.com):**  
    Forespørselsskjema → CRM “Inquiry” → auto-e-post m/ priser \+ **Stripe** deposit-lenke → hvis betalt → send kalenderinvitasjon \+ husregler → opprett oppgaver for vask/overlevering.

# **C) Rask implementeringsrekkefølge (1–2–3)**

1. **Grunnmur:** domener, Cal.com, CRM (GHL/HubSpot), Make, Brevo/Klaviyo, Slack, Airtable.

2. **Kanaler:** Manychat (IG/Messenger), Meta CAPI (server-side), GA4/Mixpanel.

3. **Flows:** bygg de 5 over \+ maler (DM, e-post, SMS), pipelines, dashboards.

# **D) “AI som lærer AI” i praksis (enkelt startoppsett)**

* **LangChain \+ LlamaIndex** på egne dokumenter (SOP, tilbud, scripts).

* **Agent**: *Lead Triage Agent* (klassifiser henvendelser, foreslå svar), *Follow-up Agent* (foreslår neste steg \+ mal).

* **Human-in-the-loop:** godkjenn i Slack før utsendelse de første ukene.

# **E) Små, viktige råd (Norge/EU)**

* Bruk **Make** (EU-databehandling) der du kan.

* Sett opp **CMP/Consent Mode v2** på nettsider for lovlig sporing.

* Malverk i norsk \+ engelsk, og hold én **Airtable “Brand Hub”** for alle brands.

Hvis du vil, kan jeg lage:

* konkrete **Make-scenarier** (eksportbare),

* en **Manychat-flow** (JSON), og

* CRM-pipelines (steg \+ felter) — alt klart til å lime inn.

