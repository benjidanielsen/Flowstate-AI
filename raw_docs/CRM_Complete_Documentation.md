
# Affiliate Network Marketing CRM - Komplett Dokumentasjon

Denne filen kombinerer **Blueprint (oversikt)** og **Full Specs (detaljer)** for CRM-systemet. 
Den er laget for at AI-modeller skal kunne lese, forstå koblinger, og bygge systemet uten å mangle informasjon.

---

# 📖 1. Pipeline

### Felter
- ID (Auto)
- Navn
- Kontaktkanal (FB, IG, LI, WA, Annet)
- Status (Ny, Venter svar, Video sendt, Webinar, Møte booket/IntroCall, No-show, På oppfølging, Ikke interessert, Dødt lead, Kunde, Team)
- Relasjonsnivå (AI 1–5)
- Interessegrad (AI 1–5)
- Neste steg (Send video, Book IntroCall, Inviter til webinar, Følg opp, Avslutt)
- Sist kontakt (Dato)
- Notater
- Prioritet (A/B/C auto fra AI)
- Kilde (FB, IG, LI, WA, Annet)

### Logikk
- Auto-prioritet: `=IF(AND(F2>=4,G2>=4),"A",IF(OR(F2>=3,G2>=3),"B","C"))`
- Conditional formatting:  
  - >7 dager uten kontakt = Rød  
  - Status = No-show = Gul  
  - Skeptiske leads = Oransje  

### Eksempeldata
| ID | Navn       | Status       | Relasjon | Interesse | Neste steg   | Sist kontakt | Notater                |
|----|------------|--------------|----------|-----------|--------------|--------------|------------------------|
| 1  | John Doe   | Ny           | 2        | 3         | Send video   | 07.09.2025   | Initial outreach email |
| 2  | Jane Smith | Video sendt  | 3        | 4         | Book Intro   | 08.09.2025   | Engaged after first vid|
| 3  | Mary J.    | Webinar      | 4        | 5         | Follow up    | 09.09.2025   | Very positive feedback |

---

# 📖 2. Historikk

### Felter
- Lead (link til Pipeline)
- Dato
- Aktivitetstype (Invitasjon, Oppfølging, Video, Webinar, IntroCall, Kunde, Nei)
- Kommentar

### Eksempeldata
- John Doe | 07.09.2025 | Invitasjon | "Intro message sent"
- Jane Smith | 08.09.2025 | Video | "Watched 80% of video"
- Mary J. | 09.09.2025 | Webinar | "Asked questions during Q&A"

---

# 📖 3. Kundekort

### Funksjoner
- Viser 1 lead basert på ID
- Felter vist: Navn, Status, Relasjon (AI), Interesse (AI), Neste steg, Notater, Win/Loss
- Historikk logg: `FILTER(Historikk!A:D, Historikk!A:A=Valgt_ID)`
- Rediger Status/Relasjon/Interesse/Neste steg/Notater direkte → oppdaterer Pipeline
- "Neste oppgave"-knapp: `=INDEX(FILTER(Pipeline!A:A,Pipeline!K:K="A"),1)`
- "Tilbake til Dashboard"-knapp

---

# 📖 4. Dashboard

### KPI-bokser
- Nye leads: `=COUNTIF(Pipeline!C:C,"Ny")`
- Video sendt: `=COUNTIF(Pipeline!C:C,"Video sendt")`
- Webinar: `=COUNTIF(Pipeline!C:C,"Webinar")`
- IntroCall: `=COUNTIF(Pipeline!C:C,"Møte booket/IntroCall")`
- No-shows: `=COUNTIF(Pipeline!C:C,"No-show")`
- Skeptiske: `=COUNTIF(Pipeline!C:C,"På oppfølging")`
- Nye kunder: `=COUNTIF(Pipeline!C:C,"Kunde")`
- Nye team: `=COUNTIF(Pipeline!C:C,"Team")`
- Nei: `=COUNTIF(Pipeline!C:C,"Ikke interessert")+COUNTIF(Pipeline!C:C,"Dødt lead")`

### Targets
- Invites: 20 per dag  
- Follow-ups: 30 per dag  
- Møter: 5 per dag  

### Andre funksjoner
- Revenue Potential: `=SUMIF(Pipeline!C:C,"Kunde",Pipeline!E:E)`
- Conversion Rate: `=COUNTIF(Pipeline!C:C,"Kunde")/COUNTA(Pipeline!A:A)`
- Reminder-liste: Leads >7 dager uten kontakt
- Pipeline Health Score: Aktive vs inaktive leads

### Grafer
- Statusflow (stolpe)
- Prioritet (kake)
- Win/Loss (søyle)
- Fremdrift 90 dager (linje)
- IPA måloppnåelse (bar)

### AI-ticker (eksempler)
- "Følg opp Kari Hansen (Video sendt 2 dager siden)"
- "Ola Nordmann møtte ikke – følg opp i kveld"
- "Du har 14 invites i dag, mål er 20 (70%)"
- "Consistency beats intensity 👊"

### Navigasjon
- Knapper til: Pipeline, Kundekort, Tracker, Leaderboard, Coach, Win/Loss, IPA
- Reset/Import/Eksport-knapper

---

# 📖 5. 90-dagers Tracker

### Felter
- Dag
- Dato
- Invitasjoner
- Oppfølginger
- Presentasjoner
- Nye kunder
- Nye team
- Kommentar

### Logikk
- Auto-dato: `=Startdato + ROW()-1`
- Conditional formatting: <10=rød, 10–20=gul, 20+=grønn
- Progress bar: `=TODAY()-Startdato`

### Eksempeldata
| Dag | Dato       | Invites | Follow-ups | Presentasjoner | Nye kunder | Nye team | Kommentar |
|-----|------------|---------|------------|----------------|------------|----------|-----------|
| 1   | 07.09.2025 | 5       | 2          | 0              | 0          | 0        | Slow start|
| 2   | 08.09.2025 | 15      | 10         | 1              | 0          | 0        | Better day|
| 3   | 09.09.2025 | 20      | 25         | 2              | 1          | 0        | Closed 1  |

---

# 📖 6. Leaderboard

### Felter
- Team Member
- Total Converted
- Revenue Generated
- Rank

### Formler
- Total Converted: `=COUNTIF(Pipeline!C:C,"Kunde")`
- Revenue Generated: `=SUMIF(Pipeline!C:C,"Kunde",Pipeline!E:E)`
- Rank: `=RANK(C2,C:C)`

### Eksempeldata
| Team Member | Total Converted | Revenue Generated | Rank |
|-------------|-----------------|-------------------|------|
| John Doe    | 5               | 2500              | 1    |

---

# 📖 7. Coach

### Felter
- Dato
- Hva gikk bra?
- Hva kunne vært bedre?
- Idéer
- AI forslag

### Funksjoner
- 90 rader (daglig logg)
- AI-spørsmål daglig: "Hva fikk du til i dag?", "Hva kunne vært bedre?"
- Ukentlig rapport via pivot + AI

---

# 📖 8. Win/Loss Analyse

### Felter
- Lead (link til Pipeline)
- Status (Nei, Ikke interessert, Dødt lead)
- Årsak (Pris, Timing, Ikke interessert, Feil målgruppe)
- Kommentar

### Funksjoner
- Drop-down årsaker
- Teller med COUNTIF
- Diagram: årsak vs antall
- AI analyserer mønstre

---

# 📖 9. IPA Tracker

### Felter
- Dato
- Nye prospekter
- Oppfølginger
- Møter booket
- Møter gjennomført
- Tid brukt (min)
- Dagsmål

### Logikk
- IPA% = `(Invites+FollowUps+Møter)/Mål`
- Conditional formatting: <70%=rød, 70–90%=gul, >90%=grønn
- Ukesummer = SUMIFS

### Eksempeldata
| Dato       | Nye prospekter | Oppfølginger | Møter booket | Møter gjen. | Tid brukt | IPA% |
|------------|----------------|--------------|--------------|-------------|-----------|------|
| 07.09.2025 | 5              | 10           | 1            | 1           | 60 min    | 85%  |
| 08.09.2025 | 15             | 20           | 2            | 2            | 120 min   | 100% |

---

# 📖 10. AI Automasjon

### Funksjoner
- Lead scoring: AI setter Relasjon + Interesse
- Neste steg: AI foreslår handling
- No-show: AI legger inn oppfølging samme kveld + neste dag
- Video/Webinar: AI foreslår follow-up 20 min etter video, samme kveld etter webinar
- IPA reminders: AI ticker "Du er på 70% av målet"
- Daglig coach: AI stiller 4–6 spørsmål, logger svar
- Ukentlig rapport: AI analyserer Coach + Win/Loss
- Gamification: AI gir ekstra utfordringer
- Import: AI mapper gamle lister til riktig format
- Calendar sync: møter kobles til leads
- Push-varsler: Messenger/E-post reminders

---

