# 🌐 Flowstate-AI – Intelligent CRM / Living System

## 🧭 Purpose
Flowstate-AI is an **AI-first CRM operating system**, designed for **network marketers and solo entrepreneurs**.  
It enforces structured activity flows (Frazer Method) and integrates an **AI improvement loop**, making the system both robust and self-evolving.  

---

## 🌍 Vision
Flowstate-AI is not just a CRM.  
It is evolving into a **self-improving living system** that continuously learns, adapts, and empowers humans to reach their highest potential.  

---

## 📂 Project Structure

*(Structure will be populated as the project develops)*

---

## 🔄 Iterative Process
The system evolves through recursive process runs (100×100 → 1M×1M).  
Each iteration stress-tests design and logic, ensuring the system becomes:  

- ✅ Idiot-proof  
- ✅ Elegant  
- ✅ Scalable  
- ✅ Future-ready  

Each iteration includes:
- Backtest & Front-test  
- Cross-check (backend & frontend)  
- Stress-test (scalable simulations)  
- Refinement & re-run  
- Documentation update  

---

## 📖 Documentation Standards
- **System Design Notes** → architecture, logic flow, AI evolution  
- **Process Reports** → stress-test results  
- **Improvement Logs** → refinements per iteration  
- **Blueprints** → visuals and logic mapping  

---

## 🧩 Core Components

### Pipeline Engine
- Enforces **Frazer Method**: Talk → Invite → Show → Keep Talking  
- State-machine prevents skipping steps  
- CRUD ops on prospects stored in DB  

### Prospect Management
- Minimal input (Name, Platform)  
- Customer Card (Profile, Notes, Interactions, Next Step)  
- AI summary (relation, interest, urgency)  

### Reminder System
- **Video Sent** → 24h/48h reminders  
- **No-Show** → 2h/1d reminders  
- **Inactivity** → 7+ day reminders  
- Powered by cron jobs / schedulers  

### Dashboard
- Daily Method of Operation (DMO):  
  - 20 new conversations  
  - 30 follow-ups  
  - 5–10 invites  
  - 3–5 presentations  
- Progress bar + AI-prioritized tasks  

### Feedback & Logging
- JSON-based logs  
- Feedback button for user reports  
- Categories: **Error | Bug | Suggestion | Idea | Critical**  

### Improvement Engine
- Input: Logs + Feedback  
- Processing: Categorization, scoring, clustering  
- Output: Developer Reports (Markdown/JSON)  
- Runs **mini stress-tests** before implementing fixes  

---

## 🛠 Tech Stack
- **Frontend:** React.js + Tailwind CSS  
- **Backend:** Node.js + Express  
- **Database:** PostgreSQL (prod) / SQLite (beta)  
- **AI Layer:** Python (scoring, reminders, prioritization)  
- **Automation:** CronJobs / Task Scheduler  
- **Logging:** JSON logs + Markdown reports  

---

## 🚀 Roadmap

### Phase 1: Foundation ✅
- Core folder structure  
- Logging & documentation standards  
- Initial stress-test methodology  

### Phase 2: Blueprinting & Architecture
- Define AI core modules (input, reasoning, memory, output)  
- Design API integration points (CRM, dashboards)  
- Map UX flows in `blueprints/`  

### Phase 3: MVP
- Basic logging system  
- Simulation engine  
- First CRM-to-AI adapter  

### Phase 4: Testing & Validation
- Backtests + synthetic edge cases  
- Recursive stress-tests (1000×1000 → 1M×1M)  
- Document results  

### Phase 5: Evolved AI
- Persistent memory (vector DB)  
- Autonomous task planning  
- Reinforcement learning signals  

### Phase 6: User Layer
- Gamified UI  
- Mobile + web dashboards  
- Frazer AI assistant  

### Phase 7: Final Refinement
- Continuous improvement loop  
- Automatic refinements from logs  
- Large-scale deployment readiness  

---

## ✅ Milestones
- [ ] MVP finished  
- [ ] First AI-human test  
- [ ] First 100×1000 stress-test complete  
- [ ] Frazer AI assistant online  
- [ ] First live deployment  

---

## ⚠️ Current Limitations (Beta)
- Single-user only  
- No team-mode  
- Lightweight AI models  
- Feedback engine = limited  
- GDPR skipped in beta  

---

## 🔮 Future Extensions
- Multi-user / team collaboration  
- Predictive AI coaching  
- External CRM/social integrations  
- Enterprise-grade scalability  

---

## 📌 Summary
Flowstate-AI is a **self-refining AI-first CRM system**, designed for stress, built for evolution, and optimized for network marketers at scale.  
Every iteration strengthens both the product and the user's workflow.

---

# 🇳🇴 Norsk Utviklerrettet Produktbeskrivelse

*Flowstate-AI — Utviklerrettet produktbeskrivelse (Single-User Beta v2.1)*
*Versjon: 2025‑09‑28*

## 1) Formål og scope
Flowstate-AI er et AI‑først CRM‑lignende operativsystem for nettverksmarkedsførere og solo‑gründere. Systemet håndhever strukturert aktivitetsflyt (Frazer‑metoden: Talk → Invite → Show → Keep Talking) og inkluderer en AI‑drevet forbedringssløyfe som bruker logger og tilbakemeldinger til å foreslå konkrete utviklertiltak. Målet er et selvforbedrende, «levende» system som blir mer robust for hver iterasjon.

### Primære mål
- Streng aktivitets-/pipelineflyt (ingen hopping over steg)
- Automatiserte påminnelser og oppfølging
- AI‑drevet forbedringsmotor som analyserer logger/feedback og produserer utviklerrapporter
- Kontinuerlig selv‑raffinering via stresstester og feedback‑sløyfer

## 2) Kjernekomponenter

### 2.1 Pipeline Engine
- Håndhever Frazer‑metoden med state‑machine‑logikk som forhindrer steg‑hopp
- Gyldige steg (ordnet): Nytt Lead → Relationship Building → Invited → Qualified → Presentation Sent → Follow-up → Team Member
- Persistens: CRUD på prospekter i DB (PostgreSQL / SQLite i beta)

### 2.2 Prospect Management
- Minimal input (f.eks. navn, plattform)
- Kundekort: Profile · Notes · Interactions · Next Step
- AI‑oppsummering pr. prospect (relasjonsstyrke, interesse, hastverk) – lettvektsmodell i beta

### 2.3 Reminder System
Triggere:
- **Video Sent** → 24h / 48h påminnelser
- **No‑Show** → 2h / 1d
- **Inaktivitet** → 7+ dager

Planlegges via cron / task scheduler.

### 2.4 Dashboard (Frontend)
Viser DMO‑mål:
- 20 nye samtaler
- 30 oppfølginger
- 5–10 invitasjoner
- 3–5 presentasjoner

Progress bar for måloppnåelse.  
AI‑prioritert oppgaveliste / Next Best Action (NBA).

### 2.5 Feedback & Logging
- JSON‑basert eventlogg
- Feedback‑knapp tilgjengelig overalt
- Kategorier: Error | Bug | Suggestion | Idea | Critical
- Logges til DB og mates inn i Improvement Engine

### 2.6 Improvement Engine
- **Input:** Logs + Feedback
- **Prosess:** Kategorisering, prioritetsscore og klustring
- **Output:** Utviklerrapport (Markdown/JSON) med:
  - Critical (umiddelbar fiks)
  - High (høy prioritet)
  - Medium/Low (forbedringer/forslag)
- **Designmål:** Kjør mini‑stresstester på foreslåtte endringer før aksept

## 3) Arkitektur og teknologier
- **Frontend:** React.js + Tailwind CSS
- **Backend:** Node.js + Express
- **Database:** PostgreSQL (prod) / SQLite (beta)
- **AI‑lag:** Python (reminder‑scoring, lead‑prioritering, AI‑coach)
- **Logging:** JSON‑eventer + Markdown‑rapporter
- **Automatisering:** CronJobs / Task Scheduler
- **Infra:** Cloud‑ready; mikrotjenester planlagt i senere faser
- **Policy:** Serverside TypeScript‑only for ny kode

## 4) Operativ logikk (kontrakter)

### 4.1 State‑machine og guardrails
- Ingen hopp mellom ikke‑tilstøtende steg
- Qualified krever utfylt Prospect's Why; ellers avvis transisjon med brukerfeedback
- Første overgang til Presentation Sent skal opprette én (1) follow‑up‑task (forfall ≈ +24–48h) hvis den ikke allerede finnes for samme prospect

### 4.2 Reminders (systemregler)
- **Video Sent:** 24h / 48h
- **No‑Show:** 2h / 1d
- **Inaktivitet:** 7+ dager
- **Scheduler:** Periodisk jobb evaluerer tasks/forfallsdatoer og utløser varsel/oppgave

### 4.3 NBA (Next Best Action)
UI‑funksjon som prioriterer åpne oppgaver (på tvers av prospekter) og foreslår neste handling pr. steg:
- **Nytt Lead** → Start samtale / bygg relasjon
- **Relationship Building** → Avdekk Why
- **Invited** → Bekreft invitasjon
- **Qualified** → Send presentasjon / book møte
- **Presentation Sent** → Følg opp innen 24–48 t
- **Follow‑up** → Avklar spørsmål → mot beslutning
- **Team Member** → Onboarding

## 5) Datamodeller (minimums‑kontrakter)
*Skjema kan utvides; feltene under må finnes for å oppfylle kontraktene over.*

### 5.1 Prospect
```typescript
export type Prospect = {
  id: string;                // UUID
  name: string;
  platform?: string;         // f.eks. Messenger/IG/Phone
  stage:
    | "Nytt Lead" | "Relationship Building" | "Invited"
    | "Qualified" | "Presentation Sent" | "Follow-up" | "Team Member";
  why?: string;              // påkrevd for Qualified
  notes?: string;
  relationStrength?: "low" | "med" | "high"; // AI
  interest?: "low" | "med" | "high";         // AI
  urgency?: "low" | "med" | "high";          // AI
  updatedAt: string;         // ISO
  createdAt: string;         // ISO
}
```

### 5.2 Task (Reminder)
```typescript
export type Task = {
  id: string;                // UUID
  prospectId: string;
  kind: "followup" | "noshow" | "inactivity" | "custom";
  title: string;             // "Følg opp presentasjon for <navn>"
  dueAt: string;             // ISO (typisk +24–48h fra Presentation Sent)
  createdAt: string;         // ISO
  completedAt?: string;      // ISO
}
```

### 5.3 Interaction / Logg
```typescript
export type Interaction = {
  id: string;
  prospectId: string;
  ts: string;                // ISO
  type: "note" | "status-change" | "message" | "call" | "meeting";
  payload?: any;             // f.eks. { from: "stageA", to: "stageB" }
}
```

### 5.4 FeedbackEvent
```typescript
export type FeedbackEvent = {
  id: string;
  ts: string;
  author: "user" | "system";
  level: "Error" | "Bug" | "Suggestion" | "Idea" | "Critical";
  message: string;
  context?: any;             // valgfritt
}
```

## 6) Testmetodikk (per iterasjon)
- **Stress‑testing:** Rekursive prosesskjøringer (100×100 → 1M×1M) som måler robusthet, skalerbarhet og pipeline‑integritet
- **Backtesting:** Historiske, simulerte brukerforløp
- **Front‑testing:** Edge‑cases med syntetiske data
- **Cross‑checking:** Valider backend‑logikk mot frontend‑forventninger
- **Dokumentasjon:** Logg funn → kjør forbedring → re‑run → oppdater dokumentasjon

## 7) Roadmap (faseskisser)
1. **Foundation:** mappe‑struktur, logging‑/doc‑standarder
2. **Blueprinting:** AI‑moduler (input/reasoning/memory/output), UX‑flyt, API‑kontrakter
3. **Implementation v1 (MVP):** grunnleggende logging, simulasjonsmotor, første CRM→AI‑adapter
4. **Stress Validation:** backtest + front‑test, rekursive stresstester, logging i process_logs/
5. **Implementation v2 (Evolved AI):** persistent minne (vector DB), autonom oppgaveplanlegging, RL‑signaler
6. **User‑Facing Layer:** gamifisert UI, web/mobil dashboards, «Frazer AI‑assistent»
7. **Refinement & Evolution:** kontinuerlig forbedring, automatisk arkitektur‑refaktor, klar for skala

## 8) Begrensninger (gjeldende beta)
- Single‑user (ingen team‑støtte ennå)
- Lettvekts AI‑modeller (tidlig fase)
- Feedback‑motor begrenset til kategorisering + rapporter
- GDPR ikke fullført i beta (planlagt før produksjon)

## 9) Leveransekrav ved PR (minimum)
- Følg TypeScript‑policy for ny serversidekode
- Respekter state‑machine‑reglene (ingen steg‑hopp, why før Qualified, follow‑up‑task ved Presentation Sent uten duplikater)
- Oppdater docs ved atferdsendringer (README / Process Reports / Improvement Logs)
- Legg ved testnotater: hva ble stresstestet, hva ble back/front‑testet, resultat og ev. regresjoner
- Endrer du reminders/NBA: oppdater kontraktene i denne spesifikasjonen

## 10) TL;DR
Flowstate‑AI er et selvforbedrende AI‑CRM som håndhever en streng pipeline, automatiserer oppfølging og prioriterer neste handling. Hver iterasjon logger, evaluerer og forbedrer både arbeidsflyt og produkt, slik at systemet gradvis blir idiotsikkert, elegant, skalerbart og fremtidsklart.
