**This document outlines a comprehensive prospect pipeline and activity tracking system for network marketing, designed for use in Google Sheets. It details a step-by-step flow for handling new contacts from initial connection to meeting booking and systematic follow-ups.**

The system includes:

* **Google Sheet Columns**: A list of 10 columns for tracking prospects, including Name, Contact Channel, Status, Relationship Level, Interest Level, Next Step, Last Contact Date, No-show?, Notes, and Priority (A/B/C).  
* **Prospect Flow (Step-by-Step)**: A seven-step process covering connecting and building rapport, sending videos as a fallback, follow-ups after video, webinar to 1:1 meetings, no-show handling, managing skeptical prospects, and qualification before dedicating time.  
* **System for Daily Use**: Instructions for sorting the Google Sheet by priority, working with A-priority prospects first, setting fixed follow-up times, and using conditional formatting for visual cues (e.g., red for no contact \>7 days, green for booked meetings, yellow for follow-up needed).  
* **Design Proposal for Google Sheets**: A detailed design for a "Network Marketing System" across four sheets:  
  * **Pipeline**: Table layout with design suggestions for headers, status column drop-downs with color coding, and conditional formatting for contact dates and priority.  
  * **Dashboard**: Suggestions for "tellerbokser" (counter boxes) using COUNTIF formulas for various lead statuses, and recommendations for bar and pie charts to visualize status and priority distribution.  
  * **90-dagers Tracker**: Table layout for daily tracking of invitations sent, follow-ups made, presentations booked/completed, new customers, and new partners, with design suggestions for headers, weekly background colors, and conditional formatting for invitation activity.  
  * **Team Leaderboard (Optional)**: A table for tracking team performance with design suggestions for highlighting top performers and using bar charts for weekly progress.

Key components include:

* **Prospect Pipeline:** A structured flow for handling new contacts, including stages like "Connect & Build rapport," "Video first (fallback)," "Follow up after video," and "Webinar \-\> 1:1." It also incorporates strategies for managing no-shows and skeptical prospects, and a qualification system to prioritize leads (A/B/C).  
* **Google Sheet Design:** Details 10 columns for tracking prospects (Name, Contact Channel, Status, Relationship Level, Interest Level, Next Step, Last Contact Date, No-show?, Notes, Priority) and suggests conditional formatting for visual cues (e.g., red for overdue contacts).  
* **System for Daily Use:** Instructions for prioritizing prospects, setting fixed follow-up times, and using visual indicators.  
* **Airtable-based Solution:** A comprehensive design with "Kundekort" (prospect card) for individual prospect details, a Dashboard for daily goals and alerts, a 90-day activity tracker, and an optional Team Leaderboard.  
* **Automation and AI Integration:** The system leverages Make (Integromat) for automation and the OpenAI API for AI functionalities. This includes AI-driven calculation of Relationship Level, Interest Level, and Priority based on notes, automated follow-up scheduling, and AI-generated message suggestions.  
* **Key Features:** Kanban-style pipeline visualization, gamification with progress bars, daily goal suggestions, win/loss analysis with AI insights, CSV lead import with AI mapping and auto-tagging, Google Calendar synchronization, and automated no-show follow-ups.  
* **User Experience:** Emphasizes a user-friendly interface with features like "Hent kundekort" (retrieve prospect card) and "Lag nytt kundekort" (create new prospect card) buttons, and a "ticker-style" alert system for important reminders and motivational quotes.  
* **Continuous Improvement:** Includes an "Improvements" function to capture user ideas and feedback for system refinement.  
* **IPA Focus:** Prioritizes Income Producing Activities (IPA) throughout the system, with AI coaching and weekly reviews to optimize focus on high-potential leads.  
* **Cost-Effectiveness:** Designed to utilize the Make free tier and integrate OpenAI API with user approval for technical feasibility, aiming for low costs.

# \=document starts here=

id: gpt-old-chat  
title: gpt//OLD CHAT  
path: /docs/gpt-old-chat  
version: 1.0  
last\_updated: 2025-09-29  
source\_type: note  
status: Stable  
owner: Benjamin Semerci

executive\_summary:  
  \- This document captures a conversation with ChatGPT regarding the development of a Network Marketing CRM system.  
  \- The user (Benjamin Semerci) wants a prospect-flow/pipeline schema to manage new contacts, including meeting booking, follow-ups, video fallback, and handling no-shows or skeptical prospects.  
  \- The user prefers working with Google Sheets initially, then transitions to Airtable for better automation and CRM-style features.  
  \- Key requirements include automated AI interpretation of notes for relation/interest scores, automatic follow-up scheduling, daily goals, gamification, and integration with Google Calendar.  
  \- The system should be user-friendly, highly automated, AI-driven, and cost-effective (preferably free or low-cost).  
  \- The conversation evolves to a comprehensive Airtable-based solution with Make (Integromat) for automation and OpenAI API (ChatGPT webhook) for AI functions.  
  \- Specific features include a "Kundekort" (prospect card) with AI-calculated scores, a Dashboard with daily goals and alerts, a 90-day tracker, and a Leaderboard (initially for the user only).  
  \- The system incorporates advanced follow-up logic for "dead leads" and no-shows, a "ticker-style" alert system, and AI-driven coaching.  
  \- The user emphasizes the importance of IPA (Income Producing Activity) as the core focus of the system.  
  \- The final plan outlines a full Airtable base with Prospects, Dashboard, and Improvements tables, integrated with Make for automation and OpenAI for AI features, with estimated low costs.

objectives\_scope:  
  \- \*\*Objective:\*\* To design and implement a comprehensive, automated, and AI-driven CRM system for Network Marketing, focusing on prospect management, follow-ups, activity tracking, and personal coaching.  
  \- \*\*Scope:\*\* This document details the iterative design process through a conversation with ChatGPT, covering initial requirements, proposed solutions (Google Sheets, then Airtable), specific features, automation logic, AI integration, cost considerations, and a step-by-step setup guide for the end-user.

requirements:  
  functional:  
    \- id: REQ-GOC-1.1  
      text: Create a prospect-flow/pipeline schema ("playbook") for handling new contacts from first connect to meeting booking, follow-up, video fallback, and systematic touchpoints without being pushy.  
      rationale: To provide a structured approach for managing new leads in Network Marketing.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Yes, jeg skjønner veldig godt"  
    \- id: REQ-GOC-1.2  
      text: The system must handle no-shows, skeptical persons, and those who need time.  
      rationale: To provide specific strategies for different prospect behaviors.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Yes, jeg skjønner veldig godt"  
    \- id: REQ-GOC-1.3  
      text: The system should lead prospects through video → webinar → zoom 1:1.  
      rationale: To guide prospects through a defined sales funnel.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Supert 🙌 Nå har jeg bildet:"  
    \- id: REQ-GOC-1.4  
      text: The system must include a qualification system to prioritize prospects.  
      rationale: To focus efforts on high-quality leads.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Supert 🙌 Nå har jeg bildet:"  
    \- id: REQ-GOC-1.5  
      text: The "Prospect Pipeline Sheet" (or equivalent) must include columns for Navn, Kontaktkanal, Status, Relasjonsnivå (1-5), Interessegrad (1-5), Neste steg, Dato sist kontakt, No-show? (Ja/Nei), Notater, and Prioritet (A/B/C).  
      rationale: To capture essential prospect information and enable effective segmentation.  
      source\_citations:  
        \- "\[7\] 🔹 Google Sheet \-- Kolonner"  
    \- id: REQ-GOC-1.6  
      text: Implement a "Connect & Build rapport" flow (day 0-3) starting with relationship questions, avoiding early business discussion, and transitioning to an intro video offer.  
      rationale: To establish a genuine connection before pitching.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 1\. Connect & Build rapport (dag 0–3)"  
    \- id: REQ-GOC-1.7  
      text: Implement a "Video first (fallback)" flow for prospects unable to meet immediately, sending a short intro video and setting a 48-hour follow-up.  
      rationale: To maintain engagement and provide an alternative information delivery method.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 2\. Video først (fallback)"  
    \- id: REQ-GOC-1.8  
      text: Implement a "Follow up after video" flow (T+48 hours) asking "What did you like best?" and inviting to webinar/1:1 if positive, or building more rapport if uncertain.  
      rationale: To gauge interest and guide the next steps.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 3\. Follow up etter video (T+48 timer)"  
    \- id: REQ-GOC-1.9  
      text: Implement a "Webinar \-\> 1:1" flow for webinar attendees, following up with "What resonated most?" and booking 1:1s with engaged prospects.  
      rationale: To convert webinar attendees into qualified leads.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 4\. Webinar → 1:1"  
    \- id: REQ-GOC-1.10  
      text: Implement "No-show handling" with a message offering replay or rescheduling.  
      rationale: To re-engage prospects who missed appointments.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 5\. No-show håndtering"  
    \- id: REQ-GOC-1.11  
      text: Implement a strategy for "Skeptical prospects" focusing on continued relationship building, commenting on their content, sharing value, and a soft re-pitch after 2-3 touchpoints.  
      rationale: To nurture hesitant prospects without being pushy.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 6\. Skeptiske prospects"  
    \- id: REQ-GOC-1.12  
      text: Implement "Qualification before time" where only A-prospects (interest 4-5 AND relation 3-5) get 1:1 Zoom, B-prospects are nurtured via video/webinar, and C-prospects receive sporadic touchpoints.  
      rationale: To optimize time allocation based on prospect quality.  
      source\_citations:  
        \- "\[7\] 🔹 Prospect Flow (Steg for steg), 7\. Kvalifisering før tid"  
    \- id: REQ-GOC-1.13  
      text: The system should allow sorting the Google Sheet daily by Prioritet A/B/C, prioritizing A-prospects.  
      rationale: To focus daily efforts on high-priority leads.  
      source\_citations:  
        \- "\[7\] 🔹 System for deg"  
    \- id: REQ-GOC-1.14  
      text: The system should enable setting fixed follow-up times (e.g., T+2 days after video, T+1 day after webinar).  
      rationale: To ensure consistent and timely follow-ups.  
      source\_citations:  
        \- "\[7\] 🔹 System for deg"  
    \- id: REQ-GOC-1.15  
      text: Implement Conditional Formatting in Sheets for visual cues (Red for no contact \>7 days, Green for booked meeting, Yellow for needing follow-up).  
      rationale: To provide quick visual status indicators.  
      source\_citations:  
        \- "\[7\] 🔹 System for deg"  
    \- id: REQ-GOC-1.16  
      text: The system should include an example dashboard in Google Sheets with lead counters per status and weekly bookings.  
      rationale: To provide an overview of pipeline performance.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Her er en oppdatert versjon av malen med et eksempel-dashboard innebygd"  
    \- id: REQ-GOC-1.17  
      text: The system should include a 90-day activity tracker (daily invitations, follow-ups, meetings, results).  
      rationale: To track individual and team activity and progress.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Her er en oppdatert versjon av malen med et eksempel-dashboard innebygd"  
    \- id: REQ-GOC-1.18  
      text: The system should allow changing the start date of the 90-day run, with all dates automatically adjusting.  
      rationale: To provide flexibility for recurring 90-day runs.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Nydelig 🙌 Da setter jeg opp 90-dagers-run’et slik at:"  
    \- id: REQ-GOC-1.19  
      text: The system should automatically calculate Relasjonsnivå based on contact frequency and AI interpretation of notes for tone/interest.  
      rationale: To reduce manual input and provide AI-driven insights into prospect relationships.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 2\. Automatiske felt"  
    \- id: REQ-GOC-1.20  
      text: The system should automatically calculate Interessegrad (1-5) by AI reading notes (positive/negative, open/skeptical).  
      rationale: To provide AI-driven insights into prospect interest levels.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 2\. Automatiske felt"  
    \- id: REQ-GOC-1.21  
      text: The system should automatically determine Prioritet based on a combination of Status \+ Interesse \+ Relasjon.  
      rationale: To ensure dynamic and intelligent prioritization of leads.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 2\. Automatiske felt"  
    \- id: REQ-GOC-1.22  
      text: The dashboard should display a list of prospects not contacted in X days.  
      rationale: To highlight overdue follow-ups.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 3\. Oppfølginger på dashboard"  
    \- id: REQ-GOC-1.23  
      text: The dashboard should display a list of no-shows with automatic suggestions for new follow-ups (e.g., "contact again in 3 days / 7 days").  
      rationale: To automate re-engagement with no-show prospects.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 3\. Oppfølginger på dashboard"  
    \- id: REQ-GOC-1.24  
      text: The dashboard should clearly show "Neste steg" (Next Step) for each prospect (e.g., "This person is waiting for video", "This one is waiting for follow-up call", "This one has an appointment in 2 days").  
      rationale: To provide clear guidance on immediate actions.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 3\. Oppfølginger på dashboard"  
    \- id: REQ-GOC-1.25  
      text: If a meeting date is entered (e.g., "Wednesday 19:00"), it should automatically sync to Google Calendar.  
      rationale: To integrate scheduling with the user's calendar.  
      source\_citations:  
        \- "\[7\] 🔹 Ditt ønske (oppsummert), 4\. Integrasjoner"  
    \- id: REQ-GOC-1.26  
      text: The system should support Kanban-style viewing of pipeline phases (New → Contacted → Video sendt → Møte booket → Oppfølging → Close (Ja/Nei)).  
      rationale: To provide a visual and intuitive representation of the sales pipeline.  
      source\_citations:  
        \- "\[7\] 🚀 Ditt Ultimative CRM/AI-Coach for Network Marketing, 🔹 1\. Pipeline & Gamification"  
    \- id: REQ-GOC-1.27  
      text: The system should include gamification with a progress bar showing leads in each phase.  
      rationale: To motivate users and visualize progress.  
      source\_citations:  
        \- "\[7\] 🚀 Ditt Ultimative CRM/AI-Coach for Network Marketing, 🔹 1\. Pipeline & Gamification"  
    \- id: REQ-GOC-1.28  
      text: The system should suggest daily goals (e.g., "Talk to 10 new prospects today" or "Move 5 people from cold → warm").  
      rationale: To guide daily activities and focus on key metrics.  
      source\_citations:  
        \- "\[7\] 🚀 Ditt Ultimative CRM/AI-Coach for Network Marketing, 🔹 1\. Pipeline & Gamification"  
    \- id: REQ-GOC-1.29  
      text: The system should allow logging the reason when a prospect says "No" (e.g., price, timing, not interested).  
      rationale: To enable win/loss analysis and identify patterns.  
      source\_citations:  
        \- "\[7\] 🚀 Ditt Ultimative CRM/AI-Coach for Network Marketing, 🔹 2\. Win/Loss Analyse"  
    \- id: REQ-GOC-1.30  
      text: The AI should analyze win/loss data after 30-90 days to identify patterns (e.g., "40% of losses are due to timing \-- follow up these in 3 months").  
      rationale: To provide actionable insights for improving sales strategies.  
      source\_citations:  
        \- "\[7\] 🚀 Ditt Ultimative CRM/AI-Coach for Network Marketing, 🔹 2\. Win/Loss Analyse"  
    \- id: REQ-GOC-1.31  
      text: The system must support importing 1000+ leads from Google Sheets CSV files.  
      rationale: To facilitate migration of existing prospect lists.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan importere 1000+ leads uten manuelt arbeid, 1\. Eksporter listene dine fra Google Sheets"  
    \- id: REQ-GOC-1.32  
      text: The AI should map and normalize fields during CSV import (e.g., "Navn" to column A, "Kontaktkanal" to column B).  
      rationale: To automate data cleaning and standardization.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan importere 1000+ leads uten manuelt arbeid, 3\. AI Mapper"  
    \- id: REQ-GOC-1.33  
      text: The AI should auto-tag prospects based on notes or source (e.g., "Instagram", "Cold", "Old lead").  
      rationale: To automate categorization and segmentation.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan importere 1000+ leads uten manuelt arbeid, 4\. Autotagger"  
    \- id: REQ-GOC-1.34  
      text: The system should integrate with Google Calendar (sync).  
      rationale: To connect CRM activities with scheduling.  
      source\_citations:  
        \- "\[7\] 🔹 AI som leser kalenderen din, 1\. Google Calendar Sync (gratis i Airtable)"  
    \- id: REQ-GOC-1.35  
      text: The AI should read meeting titles from Google Calendar (e.g., "WEBINAR" or "1:1 call with Ola") to understand the type of event.  
      rationale: To provide context for calendar events within the CRM.  
      source\_citations:  
        \- "\[7\] 🔹 AI som leser kalenderen din, 2\. AI leser møtetitler"  
    \- id: REQ-GOC-1.36  
      text: When an appointment is booked, it should be automatically added to the prospect's Kundekort (AI matches name in calendar with CRM).  
      rationale: To ensure prospect records are up-to-date with meeting information.  
      source\_citations:  
        \- "\[7\] 🔹 AI som leser kalenderen din, 3\. Automatisk i systemet"  
    \- id: REQ-GOC-1.37  
      text: If a prospect is a no-show, the system should automatically create a follow-up task 2-3 days later (e.g., "Follow up Ola (no-show)").  
      rationale: To automate re-engagement with missed appointments.  
      source\_citations:  
        \- "\[7\] 🔹 AI som leser kalenderen din, 3\. Automatisk i systemet"  
    \- id: REQ-GOC-1.38  
      text: The AI coach on the dashboard should provide actionable suggestions (e.g., "You have 5 no-shows from last week, follow up these today.").  
      rationale: To provide proactive guidance for daily tasks.  
      source\_citations:  
        \- "\[7\] 🔹 Dashboard & Coach"  
    \- id: REQ-GOC-1.39  
      text: The Kundekort should display a unique Prospect-ID generated by the system.  
      rationale: To uniquely identify each prospect.  
      source\_citations:  
        \- "\[7\] 🔹 Dashboard & Coach"  
    \- id: REQ-GOC-1.40  
      text: The Kundekort should include an AI-analysis field (e.g., "Relasjonsnivå: 3/5 (moderate rapport)").  
      rationale: To provide AI-driven insights into relationship strength.  
      source\_citations:  
        \- "\[7\] 🔹 Dashboard & Coach"  
    \- id: REQ-GOC-1.41  
      text: The Kundekort should include an AI-score field (e.g., "Hot %: 82% probability to book meeting.").  
      rationale: To provide AI-driven insights into prospect hotness/likelihood to convert.  
      source\_citations:  
        \- "\[7\] 🔹 Dashboard & Coach"  
    \- id: REQ-GOC-1.42  
      text: The AI should auto-generate message suggestions for follow-ups based on pipeline stage (e.g., "Video sent, no response after 2 days" \-\> "Did you get to see the video?").  
      rationale: To streamline and personalize follow-up communications.  
      source\_citations:  
        \- "\[7\] 🔹 Bonusfunksjon (som gir deg edge)"  
    \- id: REQ-GOC-1.43  
      text: The AI should generate a Daily Gameplan (e.g., via email at 08:00) with new prospects to contact, warmest leads, and tasks.  
      rationale: To provide a structured daily agenda.  
      source\_citations:  
        \- "\[7\] 🔹 Bonusfunksjon (som gir deg edge)"  
    \- id: REQ-GOC-1.44  
      text: The system should include a Daily habit tracker logging messages/calls made to visualize user habits.  
      rationale: To track and improve daily productivity.  
      source\_citations:  
        \- "\[7\] 🔹 7\. Ekstra forslag du kanskje ikke tenkte på"  
    \- id: REQ-GOC-1.45  
      text: The system should support Broadcast with tags to send targeted information (e.g., to "Fitness" or "Crypto" prospects).  
      rationale: To enable segmented communication.  
      source\_citations:  
        \- "\[7\] 🔹 7\. Ekstra forslag du kanskje ikke tenkte på"  
    \- id: REQ-GOC-1.46  
      text: The system should include a Smart AI coach providing mini-challenges (e.g., "Today: send voice message to 3 new").  
      rationale: To motivate and guide users with small, actionable tasks.  
      source\_citations:  
        \- "\[7\] 🔹 7\. Ekstra forslag du kanskje ikke tenkte på"  
    \- id: REQ-GOC-1.47  
      text: The Kundekort should have One-click actions (e.g., "Send DM on Messenger" opens Messenger directly).  
      rationale: To streamline common communication tasks.  
      source\_citations:  
        \- "\[7\] 🔹 7\. Ekstra forslag du kanskje ikke tenkte på"  
    \- id: REQ-GOC-1.48  
      text: Contact channels must include Messenger, Instagram, SMS, Snapchat, and Zoom, available as a dropdown when creating a new Kundekort. Email is not used for prospects.  
      rationale: To align with the user's preferred communication methods.  
      source\_citations:  
        \- "\[7\] Du sa: Kontaktkanal (Messenger / Instagram / SMS / Snapchat / Zoom)."  
    \- id: REQ-GOC-1.49  
      text: The system needs a "Hent kundekort" button to search for names and a "Lag nytt kundekort" button.  
      rationale: To provide quick access to existing and new prospect records.  
      source\_citations:  
        \- "\[7\] Du sa: Kontaktkanal (Messenger / Instagram / SMS / Snapchat / Zoom)."  
    \- id: REQ-GOC-1.50  
      text: The AI should drive the system, but the user must be able to provide feedback ("yes", "no", "postpone") during the first few weeks for AI to learn their style.  
      rationale: To allow for personalized AI adaptation.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Perfekt 🙌 nå har vi spikret visjonen din\!"  
    \- id: REQ-GOC-1.51  
      text: The system should include all mentioned gamification, dashboard, pipeline, reminders, habit tracker, AI-coach, win/loss analysis, and broadcast tags.  
      rationale: To deliver a comprehensive and engaging system.  
      source\_citations:  
        \- "\[7\] ChatGPT sa: Perfekt 🙌 nå har vi spikret visjonen din\!"  
    \- id: REQ-GOC-1.52  
      text: The system should display "Dagens mål" (daily goals), "dagens avtaler" (today's appointments from calendar), and "oppfølginger du må gjøre i dag" (follow-ups due today) when the dashboard is opened.  
      rationale: To provide an immediate overview of daily priorities.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 1\. Når du åpner dashboardet"  
    \- id: REQ-GOC-1.53  
      text: The AI should suggest follow-ups (e.g., "Do you want to follow up with Ola who saw the video on Tuesday but hasn't responded?"), with user options to accept ("Ja"), decline ("Nei"), or postpone ("Utsett").  
      rationale: To automate and streamline follow-up decisions.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 1\. Når du åpner dashboardet"  
    \- id: REQ-GOC-1.54  
      text: When "Ja" is pressed for an AI-suggested follow-up, the task is marked complete; "Utsett" postpones it to the next day.  
      rationale: To manage follow-up tasks efficiently.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 1\. Når du åpner dashboardet"  
    \- id: REQ-GOC-1.55  
      text: A "Hent kundekort" button should allow searching by name, opening the Kundekort in a popup.  
      rationale: To quickly access prospect details.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 2\. Når du skal jobbe med folk"  
    \- id: REQ-GOC-1.56  
      text: A "Lag nytt kundekort" button should allow filling in Navn, Kontaktkanal (dropdown), and Status.  
      rationale: To easily create new prospect records.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 2\. Når du skal jobbe med folk"  
    \- id: REQ-GOC-1.57  
      text: The Kundekort should contain Navn, Kontaktkanal (dropdown), Prospect-ID (auto-generated), Relasjonsnivå (AI-calculated, manually adjustable), Neste steg (AI-suggested, manually settable), Status, Notater, and Pipeline-posisjon.  
      rationale: To provide a comprehensive and interactive prospect view.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 2\. Når du skal jobbe med folk"  
    \- id: REQ-GOC-1.58  
      text: The AI should read user notes and suggest follow-up messages.  
      rationale: To personalize and automate message creation.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.59  
      text: Google Calendar sync should automatically fetch appointments like "Intro \- Ola (Benji)".  
      rationale: To integrate meeting data into the CRM.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.60  
      text: No-shows should trigger reminders at 12h, 24h, and 48h.  
      rationale: To automate re-engagement with missed appointments.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.61  
      text: Gamification should show the number of leads in each pipeline phase.  
      rationale: To visualize progress and motivate users.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.62  
      text: Broadcast functionality should allow filtering prospects by tags (e.g., fitness, crypto, mamma-perm).  
      rationale: To enable targeted communication.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.63  
      text: The Daily habit tracker should show the number of people contacted, new contacts, and follow-ups.  
      rationale: To provide an overview of daily activity.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.64  
      text: A Morning brief at 08:00 should provide daily goals and suggestions.  
      rationale: To start the day with clear priorities.  
      source\_citations:  
        \- "\[7\] 🔹 Hvordan det blir for deg å bruke systemet, 3\. Automatikk"  
    \- id: REQ-GOC-1.65  
      text: An "Improvements" function (or equivalent in Norwegian) should allow the user to write new ideas, desired changes, or simplifications for the system, with fields for Date, Idea, Category, and Status.  
      rationale: To enable continuous system refinement based on user feedback.  
      source\_citations:  
        \- "\[7\] Du sa: Gjerne opprett en funkjson som heter improvements"  
        \- "\[7\] 📊 Oppsettet du får i Airtable, 5\. Improvements / Forbedringer"  
    \- id: REQ-GOC-1.66  
      text: The system should provide a daily list of Kundekort that have been processed, allowing the user to review past interactions.  
      rationale: To maintain a historical record and facilitate review.  
      source\_citations:  
        \- "\[7\] Du sa: Jeg blir å trenge en dagens liste over kundekort"  
    \- id: REQ-GOC-1.67  
      text: Prospects who say "no" or are not interested should be put on a follow-up list for contact every 2 weeks and invited to the weekly Wednesday webinar at 20:00.  
      rationale: To maintain a long-term nurturing strategy for disengaged leads.  
      source\_citations:  
        \- "\[7\] Du sa: Jeg blir å trenge en dagens liste over kundekort"  
    \- id: REQ-GOC-1.68  
      text: The system must prioritize IPA (Income Producing Activity) above all other priorities except fixed calls and intro/meetings.  
      rationale: To ensure the system drives the most impactful business activities.  
      source\_citations:  
        \- "\[7\] Du sa: En annen ting jeg vil nevne for deg er IPA"  
    \- id: REQ-GOC-1.69  
      text: During the day, the system should encourage maximum IPA (most contacts, most bookings for calls/videos, new/old relationship building).  
      rationale: To maximize daily productivity.  
      source\_citations:  
        \- "\[7\] Du sa: En annen ting jeg vil nevne for deg er IPA"  
    \- id: REQ-GOC-1.70  
      text: The system should perform a weekly review of collected information to filter out prospects/leads/follow-ups without potential, focusing on those with an open mindset and engagement.  
      rationale: To optimize focus on promising leads.  
      source\_citations:  
        \- "\[7\] Du sa: En annen ting jeg vil nevne for deg er IPA"  
    \- id: REQ-GOC-1.71  
      text: The AI should send "How was the last hour?" questions 4-6 times a day.  
      rationale: To provide frequent self-reflection and coaching.  
      source\_citations:  
        \- "\[7\] Du sa: Gjerne la AI sende 4-6 ganger om dagen"  
    \- id: REQ-GOC-1.72  
      text: The system should use Make (Integromat) free tier for automation.  
      rationale: To leverage a cost-effective automation platform.  
      source\_citations:  
        \- "\[7\] Du sa: Jeg vil bruke Make (Integromat) free tier"  
    \- id: REQ-GOC-1.73  
      text: The system should integrate Airtable with OpenAI API via Webhook for AI functions, with the user's approval if technically feasible without stress.  
      rationale: To enable advanced AI capabilities.  
      source\_citations:  
        \- "\[7\] Du sa: Jeg har ingen erfaring med å koble Airtable → OpenAI API."  
    \- id: REQ-GOC-1.74  
      text: The dashboard should show "Dagens kundekort gjennomført" (today's processed prospect cards) allowing review of who was contacted.  
      rationale: To provide a daily activity log.  
      source\_citations:  
        \- "\[7\] 🚀 Oppsummering av ditt system, 📌 Kjerneelementer, Dagens liste / Historikk"  
    \- id: REQ-GOC-1.75  
      text: The AI should log time spent per Kundekort.  
      rationale: To track time efficiency.  
      source\_citations:  
        \- "\[7\] 🚀 Oppsummering av ditt system, 📌 Kjerneelementer, Dagens liste / Historikk"  
    \- id: REQ-GOC-1.76  
      text: Follow-ups for "no-shows" should be timed based on the meeting time (day meeting \-\> same evening; evening meeting \-\> next day 12:00 or 16:00).  
      rationale: To optimize follow-up timing for no-shows.  
      source\_citations:  
        \- "\[7\] Du sa: For no shows \\\\\\"Ny reminder dagen etter (12:00 eller 16:00).\\\\\\""  
    \- id: REQ-GOC-1.77  
      text: All invited webinar attendees should be followed up immediately after the Wednesday webinar at 20:00.  
      rationale: To capitalize on immediate post-webinar engagement.  
      source\_citations:  
        \- "\[7\] Du sa: En annen ting er at etter onsdags webinaret"  
    \- id: REQ-GOC-1.78  
      text: Reminders for everything should be implemented.  
      rationale: To ensure no task is missed.  
      source\_citations:  
        \- "\[7\] Du sa: Ikke glem påminnelser til absolutt alt"  
    \- id: REQ-GOC-1.79  
      text: Alerts should "float and change like news on a crypto site" on the dashboard/main page, showing important reminders, quotes, or NWM/business-related information for 10-second intervals.  
      rationale: To provide dynamic and highly visible alerts.  
      source\_citations:  
        \- "\[7\] Du sa: og gjerne opprett noe der alerts kan sveve"  
    \- id: REQ-GOC-1.80  
      text: Reminder pushes should be sent via both email and Messenger bot, and appear on the dashboard/main page, following the user throughout the system.  
      rationale: To ensure comprehensive and persistent notification delivery.  
      source\_citations:  
        \- "\[7\] ifht Reminder-pushes (via e-post eller Messenger bot \-- du velger)."  
    \- id: REQ-GOC-1.81  
      text: The AI should adjust follow-up frequency for "dead leads" based on non-response, gradually increasing intervals (1 week \-\> 2 weeks \-\> 3 weeks \-\> max 2 months), with leads remaining in the system for at least 5 years.  
      rationale: To optimize engagement with less responsive leads over the long term.  
      source\_citations:  
        \- "\[7\] 🔄 Oppdatert logikk, 🟡 \\"Døde\\" leads"  
    \- id: REQ-GOC-1.82  
      text: The AI should suggest quotes or mini-push messages on the alert ticker (e.g.,

