# NWM/CRM — Zero‑Based Funksjonell Spesifikasjon  
**Leveransesjekkliste (verktøy‑agnostisk, 1 side)**

**Bruk:** Kopiér inn i leveransen eller bruk som “sign‑off”. Kryss av når hvert punkt er levert.  
**Prinsipp:** Tenk fra blanke ark. Ingen verktøy-binding. Enkelt, dupliserbart, IPA‑først.

---

## A. Executive Summary
- [ ] 10–12 punkter som forklarer mål, rammer og hovedvalg.
- [ ] Tydelig målgruppe + primærbruker (distributør/leder).
- [ ] Antakelser og begrensninger eksplisitt listet.

## B. Issue‑log (Audit)
- [ ] Tabell: Problem • Alvorlighet • Anbefalt fix • Status.
- [ ] De 5 største risikoene (inkl. compliance) er tydelig adressert.

## C. Målarkitektur (verktøy‑agnostisk)
- [ ] Overordnet arkitekturdiagram (tekst/Mermaid/ASCII).
- [ ] Forklaring av dataflyt og ansvar (hvem gjør hva, når, hvorfor).
- [ ] “3‑klikk til Neste Oppgave” prinsippet dokumentert.

## D. Datamodell & Tilstandsmaskin
- [ ] Entiteter: Prospect, Aktivitet, Avtale, Follow‑up, Notat, Status, Score, Pipeline‑steg, Mål/Vane, Win/Loss, Team/Pod.
- [ ] Feltliste pr. entitet (nøkler, tillatte verdier, påkrevde felt).
- [ ] Tilstandsmaskin: lovlige overganger + hendelser (med rasjonale).

## E. Brukerreiser (min. 3 varianter)
- [ ] Hver flyt beskrevet E2E (triggere → milepæler → beslutning → utfall).
- [ ] Diagram per flyt (tekst/Mermaid).
- [ ] Sett med nye, egne varianter (ikke bare skissen):  
  - Connect → Video → Intro (1:1) → Beslutning → Onboarding *(eksempel)*  
  - Webinar: Invitasjon → Deltakelse → Oppfølging → Konvertering *(eksempel)*  
  - Retensjon: 30‑dagers oppfølging → Community → Ambassadør *(eksempel)*

## F. Automatiseringsregler (plattform‑nøytrale)
- [ ] **No‑show:** oppfølging samme dag etter **2–6 t**, + **neste dag** (12:00/16:00).
- [ ] **Video sendt:** sjekk etter ca. **24 t** (justerbar).
- [ ] **“Nei takk”/kaldt:** intervaller 1 uke → 2 uker → 1 mnd → 2 mnd (nedprioriter, ikke slett).
- [ ] **IPA‑coach:** daglige mål **20 nye** + **30 follow‑ups**, morgenbrief **08:00 Europe/Oslo**, **4–6 mikropinger** per dag.
- [ ] **Kalenderforståelse:** regler for å koble møtetitler (f.eks. “Intro – [Navn]”) til riktig prospect og riktig oppfølging.

## G. Scoring & Next Best Action
- [ ] Regler for **Interesse (1–5)**, **Relasjon (1–5)**, **Prioritet (A/B/C)**.
- [ ] Tidsforfall/decay + tie‑breakers dokumentert.
- [ ] Algoritme for oppgavekø (Next Best Action) beskrevet trinnvis.

## H. Meldingsbibliotek (krav, ikke plattform)
- [ ] Malstruktur (tone, variabler, kort/lang).
- [ ] Dekker: warm/cold invite, T‑24/T‑2, post‑presentasjon, innvendinger (“har ikke tid”, “må tenke”), closing, retensjon/ambassadør.
- [ ] Compliance‑markører (inntekts‑disclaimer, reklame‑merking) angitt.

## I. KPI‑rammeverk & Eksperimenter
- [ ] Mål: **≥70% show‑rate**, **20–30% close** på kvalifiserte, **6/7 DMO‑dager**.
- [ ] Ukentlig/kvartalsvis review‑frekvens definert.
- [ ] A/B‑plan per brukerreise (hypotese, måltall, stoppkriterier).

## J. Akseptkriterier & Testplan
- [ ] Akseptkriterier per kjernefunksjon (tydelige “pass/fail”).
- [ ] Testdata (syntetiske tabeller) og teststeg (UAT).
- [ ] Exit‑criteria for v1 (MVP) beskrevet.

## K. Roadmap 30/60/90
- [ ] v1 (MVP): kjerneflyt, scoring, Next Best Action, grunnleggende meldinger.
- [ ] v1.1 (stabilitet): ytelse, datakvalitet, opprydding, “edge‑cases”.
- [ ] v2 (skala/AI‑assistanse): avansert scoring, anbefalinger, community‑loop.

## L. Alternativer & Trade‑offs
- [ ] **Tre helhetlige systemvarianter (A/B/C)** med trade‑offs (resultat, kompleksitet, vedlikehold).
- [ ] Tydelig **anbefaling** av én default og hvorfor.

## M. Compliance & Personvern (høy‑nivå)
- [ ] Inntekts‑disclaimer & reklame‑merking definert.
- [ ] Samtykke/opt‑out‑rutiner og dataretensjon spesifisert.
- [ ] Rolleforståelse (behandlingsansvarlig/databehandler) og minimisering.

## N. Brukbarhet & Team‑duplisering
- [ ] “3‑klikk til Neste Oppgave” verifisert.
- [ ] Onboarding‑guide for nye brukere (første 48 t).
- [ ] Prosess for å duplisere systemet til et nytt team/pod.

## O. Åpne antakelser & hull
- [ ] Liste over antakelser med **plan for validering**.
- [ ] Avhengigheter og “blocked by” dokumentert.
- [ ] Endringslogg (versjon, dato, hva som ble endret).

---

**Sign‑off:**  
Dato: __________  Versjon: ________  Forfatter: __________  Revidert av: __________
