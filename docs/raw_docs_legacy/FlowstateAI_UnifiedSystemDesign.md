id: flowstate-ai-unified-system-design  
title: (NY) Flowstate-AI Unified System Design Document  
path: /docs/flowstate-ai-unified-system-design  
version: 1.0  
last\_updated: 2025-09-29  
source\_type: design  
status: Stable  
owner: Not specified

executive\_summary:  
  \- This document consolidates requirements, non-functional requirements, decisions, assumptions, questions, risks, and tasks for the Flowstate-AI project.  
  \- The project aims to develop an AI-first CRM operating system for network marketers and solo entrepreneurs.  
  \- It emphasizes structured activity flows based on the Frazer Method and integrates a self-evolving AI improvement loop.  
  \- Core principles include simplicity, IPA-focus, daily goals, automation-driven processes, gamification, and GDPR compliance.  
  \- The system architecture comprises a User Interface (Action-Board), Backend & AI Engine (Prospect Hub, AI Assistant, Automation Module, Reporting & Analytics), and an Integration Layer (Google Calendar Sync, CSV Import/Export).  
  \- Development is planned in three phases: Core CRM Functionality (completed), Frazer Pipeline Rebuild & Enhanced AI, and Automation & Self-Evolving AI Loop.  
  \- Key decisions prioritize a unified Master Build File, functionality over specific brands, and explicit user approval for automated actions.  
  \- Several open questions and gaps exist, particularly around AI implementation, detailed specifications for the improvement loop, and measurable criteria for NFRs.  
  \- Technical standards include CI/CD automation with human approval, branch protection, CODEOWNERS, and comprehensive documentation.

objectives\_scope:  
  \- \*\*Objective:\*\* To provide a clear and reconciled view of the system design for the Flowstate-AI project, highlighting critical information and identifying areas that require further specification.  
  \- \*\*Scope:\*\* This document serves as a consolidated and normalized repository of requirements, non-functional requirements, decisions, assumptions, questions, risks, and tasks extracted from provided documentation for the Flowstate-AI project. It covers project context, core principles, structured extracts from source documents, system architecture, data flow, roadmap, and implementation strategy.

requirements:  
  functional:  
    \- id: REQ-1.1.1  
      text: Implement a Daily Method of Operation (DMO) including: Talk to People, Invite Them, Show Them, Keep Talking to Them.  
      rationale: Core to the Frazer Brookes recruiting plan.  
      source\_citations:  
        \- "\[1\] Section 1"  
    \- id: REQ-1.1.2  
      text: Integrate Self-Leadership and Time Management: Set Time, Protect Time, Use Affirmations, Track Progress (activity-based).  
      rationale: Essential for consistent daily action and personal effectiveness.  
      source\_citations:  
        \- "\[1\] Section 2"  
    \- id: REQ-1.1.3  
      text: Implement a Prospecting System: Define Ideal Prospect ("Who"), Find Prospects ("Where"), and Daily Action Plan ("What").  
      rationale: Structured approach to identifying and engaging potential leads.  
      source\_citations:  
        \- "\[1\] Section 3"  
    \- id: REQ-1.1.4  
      text: Implement Four Types of Conversations with specific scripts for each group: Known (never spoken), Known (haven't spoken in a while), Followers, New People (Who, Where system).  
      rationale: Tailored communication strategies for different prospect relationships.  
      source\_citations:  
        \- "\[1\] Section 2, NUMBER TWO"  
    \- id: REQ-1.1.5  
      text: Implement the "Ping-Pong" Method for relationship building, aiming for 3-5 back-and-forth messages before business discussion.  
      rationale: Builds rapport and avoids premature sales pitches.  
      source\_citations:  
        \- "\[1\] Section 3, NUMBER TWO"  
    \- id: REQ-1.1.6  
      text: Integrate a Three-Question Funnel for qualifying prospects: Ask the question, Ask "Why", Ask "What".  
      rationale: Efficiently identifies qualified leads.  
      source\_citations:  
        \- "\[1\] Section 2, NUMBER THREE"  
    \- id: REQ-1.1.7  
      text: Provide transition questions to move from chat to business discussion (e.g., "Just curious...", "Options", "Pain").  
      rationale: Facilitates natural progression from casual conversation to business.  
      source\_citations:  
        \- "\[1\] Section 3, NUMBER THREE"  
    \- id: REQ-1.1.8  
      text: Implement a presentation system focusing on three core prospect questions: "What do I actually do?", "Can I do it?", "What if I succeed?".  
      rationale: Addresses key concerns of prospects during a presentation.  
      source\_citations:  
        \- "\[1\] Section 1, NUMBER FOUR"  
    \- id: REQ-2.1.1  
      text: All code execution (build, test, deploy) must be automated via CI/CD pipelines, triggered by explicit human approval.  
      rationale: Ensures controlled and consistent deployment.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 1, 2; SVAR FRA COPILOT"  
    \- id: REQ-2.1.2  
      text: Automated pull and push of files should be set up via CI/CD, triggered by human action (push/PR/Approve).  
      rationale: Maintains version control and controlled code changes.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 2; SVAR FRA COPILOT"  
    \- id: REQ-2.1.3  
      text: Backend development should be prioritized before frontend, with a clear understanding of frontend requirements.  
      rationale: Establishes a solid foundation before building the user interface.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 4"  
    \- id: REQ-2.1.4  
      text: To-do lists must be self-generated step-by-step for each project phase and updated upon each approved PR.  
      rationale: Ensures clear task management and progress tracking.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 5"  
    \- id: REQ-2.1.5  
      text: All functionalities must be error-free and stress-tested before advancing to the next project phase.  
      rationale: Guarantees system stability and reliability.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 6"  
    \- id: REQ-2.1.6  
      text: Adherence to project roadmap, README, and other MD files is critical; scope changes require explicit documentation via REDBULL-PR.  
      rationale: Maintains project alignment and formalizes scope changes.  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, 7; SVAR FRA COPILOT"  
    \- id: REQ-2.1.7  
      text: Large changes (\>50% codebase or sensitive schema changes) require a PR marked "BREAKING" and explicit owner approval.  
      rationale: Manages significant changes with appropriate oversight.  
      source\_citations:  
        \- "\[2\] SVAR FRA COPILOT, Store endringer"  
    \- id: REQ-2.1.8  
      text: A "REDBULL" command/PR prefix acts as an admin override for changing rules, steering course, or overriding the project. Requires owner approval and extra admin review/GitHub secret token.  
      rationale: Provides an emergency override mechanism with strict controls.  
      source\_citations:  
        \- "\[2\] REDBULL — admin-override policy"  
    \- id: REQ-2.1.9  
      text: Document rules in RULES.md at the repository root.  
      rationale: Centralizes and makes project rules easily accessible.  
      source\_citations:  
        \- "\[2\] Tekniske håndhevelser"  
    \- id: REQ-2.1.10  
      text: Set up branch protection on main: require PR reviews, status checks, and disable direct pushes.  
      rationale: Ensures code quality and stability of the main branch.  
      source\_citations:  
        \- "\[2\] Tekniske håndhevelser"  
    \- id: REQ-2.1.11  
      text: Use CODEOWNERS to require owner approval for specific folders (e.g., docs/, infra/, src/backend).  
      rationale: Designates responsibility and ensures expert review for critical areas.  
      source\_citations:  
        \- "\[2\] Tekniske håndhevelser"  
    \- id: REQ-2.1.12  
      text: Implement GitHub Actions for CI jobs (build/test/stress) and a special redbull-handler workflow.  
      rationale: Automates continuous integration and provides a dedicated workflow for overrides.  
      source\_citations:  
        \- "\[2\] Tekniske håndhevelser"  
    \- id: REQ-3.1.1  
      text: The AI will gather information from 3 documents to build the best AI-driven CRM system for Network Marketing with automation.  
      rationale: Foundation for AI's knowledge base.  
      source\_citations:  
        \- "\[3\] Description of end product"  
    \- id: REQ-3.1.2  
      text: The CRM system must be an all-in-one solution for Network Marketing, minimizing admin and maximizing Income Producing Activity (IPA).  
      rationale: Core value proposition for network marketers.  
      source\_citations:  
        \- "\[3\] C.1: Visjon for systemet"  
    \- id: REQ-3.1.3  
      text: The system should be intuitive and based on principles from leaders like Frazer Brookes.  
      rationale: Ensures user-friendliness and adherence to proven methodologies.  
      source\_citations:  
        \- "\[3\] C.1: Visjon for systemet"  
    \- id: REQ-3.1.4  
      text: The system must have a built-in AI assistant without external API costs initially.  
      rationale: Cost-effective and integrated AI solution.  
      source\_citations:  
        \- "\[3\] C.1: Visjon for systemet; B: Grunnleggende Prinsipper"  
    \- id: REQ-3.1.5  
      text: The Dashboard ("Action-Board") must be 100% action-oriented, featuring daily goals (20 new contacts, 30 follow-ups) with progress bars, and a dynamic action list of 5-10 top-priority contacts sorted by AI-score.  
      rationale: Drives user activity and focuses on high-impact tasks.  
      source\_citations:  
        \- "\[3\] C.2: Dashboardet (\\"Action-Board\\")"  
    \- id: REQ-3.1.6  
      text: The CRM must include a "Kundekort" (pop-up window) with all contact information, an "Analyser & Oppdater" button to update scores and suggest next actions, and a timeline of interactions.  
      rationale: Provides a comprehensive view and interaction point for each prospect.  
      source\_citations:  
        \- "\[3\] C.3: Kundekortet"  
    \- id: REQ-3.1.7  
      text: The "Prospect Hub" (database) must feature a "Notatfelt" for AI analysis, and AI-generated fields for Relation-Score and Interest-Score.  
      rationale: Enhances prospect data with AI-driven insights.  
      source\_citations:  
        \- "\[3\] C.4: Databasen (\\"Prospect Hub\\")"  
    \- id: REQ-3.1.8  
      text: The Dashboard should include a Pipeline View showing prospects in each stage, an Activity-feed, and Top Priorities based on AI-score.  
      rationale: Provides a holistic overview of prospect management.  
      source\_citations:  
        \- "\[3\] D: Komplett Funksjonsspesifikasjon"  
    \- id: REQ-3.1.9  
      text: Contact and prospect handling must include Tagging and Segmentering with custom tags, and Advanced Search capabilities.  
      rationale: Facilitates organization and efficient retrieval of prospects.  
      source\_citations:  
        \- "\[3\] D: Komplett Funksjonsspesifikasjon"  
    \- id: REQ-3.1.10  
      text: AI & Automation features: AI-driven Coaching (pop-up messages), "No-show" Handling (auto-create follow-up tasks), and Automatic Video-oppfølging (auto-create 48h follow-up task).  
      rationale: Automates common tasks and provides proactive guidance.  
      source\_citations:  
        \- "\[3\] D: Komplett Funksjonsspesifikasjon"  
    \- id: REQ-3.1.11  
      text: Implement a Kundekort (pop-up) with auto-generated Prospect-ID, Contact Channel, Status (dropdown), Next Step (AI suggested), Notes (with AI learning), Relation Level (AI-calculated 1-5), and AI-score (e.g., "Probability to book introcall \= 73%").  
      rationale: Detailed and AI-enhanced prospect information.  
      source\_citations:  
        \- "\[3\] 3\. Kundekort (klikk på navn → popup)"  
    \- id: REQ-3.1.12  
      text: Implement automatic reminders for follow-ups (post-meeting, no-shows, inactivity \> 7 days) and a Morning Brief (08:00 email/dashboard) with critical tasks.  
      rationale: Ensures timely follow-ups and keeps users informed of priorities.  
      source\_citations:  
        \- "\[3\] 4\. Påminnelser & rapporter"  
    \- id: REQ-3.1.13  
      text: Implement an AI Follow-up assistant with message suggestions based on status (e.g., "Video sent, 2 days no response") and learning from user's tone/style.  
      rationale: Personalizes and streamlines follow-up communications.  
      source\_citations:  
        \- "\[3\] 5\. AI Follow-up assistent"  
    \- id: REQ-3.1.14  
      text: Implement CSV import of old lists with AI mapping to auto-detect columns, merge formats, and assign unique IDs.  
      rationale: Facilitates migration of existing data.  
      source\_citations:  
        \- "\[3\] 6\. Import av gamle lister"  
    \- id: REQ-3.1.15  
      text: Include a Daily habit tracker, Broadcast with tags, Smart AI coach (mini-challenges), and One-click actions in the Kundekort (e.g., "Send DM on Messenger").  
      rationale: Enhances user engagement and productivity.  
      source\_citations:  
        \- "\[3\] 7\. Ekstra forslag du kanskje ikke tenkte på"  
    \- id: REQ-3.1.16  
      text: Implement a Google Calendar Sync for appointments, with AI recognition of meeting titles and automatic follow-up reminders based on meeting status (No-show, Gjennomført).  
      rationale: Integrates with existing tools and automates post-meeting tasks.  
      source\_citations:  
        \- "\[3\] 1\. Kalender-integrasjon"  
    \- id: REQ-3.1.17  
      text: The Dashboard should display real-time daily goals (AI-set), today's appointments, a follow-up list (AI-suggested), Pipeline Gamification, and Win/Loss analysis.  
      rationale: Provides a dynamic and comprehensive daily overview.  
      source\_citations:  
        \- "\[3\] 2\. Dashboard (oversikt på ett sted)"  
    \- id: REQ-4.1.1  
      text: The final deliverable must merge old and new system descriptions plus code into one unified, build-ready system.  
      rationale: Ensures a cohesive and complete system.  
      source\_citations:  
        \- "\[4\] Code GPT sa, So the job is not \\"summarize\\" but assemble"  
    \- id: REQ-4.1.2  
      text: The Master Build File must act as a Blueprint (concept \+ architecture), Functional specification (features \+ logic), Implementation guide (step-by-step, with AI \+ automation flows), and an Improvement log section.  
      rationale: Provides a comprehensive and multi-faceted master document.  
      source\_citations:  
        \- "\[4\] Code GPT sa, And then compile into one Master Build File (.md)"  
    \- id: REQ-4.1.3  
      text: The Master Build File must include: Principles & Purpose, System Components (Dashboard, Kundekort, Prospect Hub, AI Automation), Daily Goals, Gamification, Pipeline logic, AI scoring \+ follow-ups (2–6h no-show, 24/48h video checks, inactivity reminders), Data import (CSV \+ AI mapping), Calendar sync & notification rules, and an Improvement Tracker.  
      rationale: Defines the essential content of the Master Build File.  
      source\_citations:  
        \- "\[4\] Code GPT sa, My proposal: I can generate a new \\"Master CRM Build File\\""  
    \- id: REQ-5.1.1  
      text: The system should have a sidebar with main navigation (Dashboard, Pipeline, Activity Log) and a "Nytt kundekort" button.  
      rationale: Provides essential navigation and quick access to new prospect creation.  
      source\_citations:  
        \- "\[5\]"  
    \- id: REQ-5.1.2  
      text: The system must include a search input for prospects with real-time results.  
      rationale: Enables efficient searching and retrieval of prospect information.  
      source\_citations:  
        \- "\[5\]"  
    \- id: REQ-5.1.3  
      text: Implement toast notifications for user feedback.  
      rationale: Provides non-intrusive feedback to the user.  
      source\_citations:  
        \- "\[5\] function showToast"  
    \- id: REQ-5.1.4  
      text: Implement modal windows for prospect cards.  
      rationale: Provides a focused view for prospect details.  
      source\_citations:  
        \- "\[5\] function renderModalCard"  
    \- id: REQ-5.1.5  
      text: State management: save and load appData to/from localStorage.  
      rationale: Persists user data locally for a consistent experience.  
      source\_citations:  
        \- "\[5\] // \---------------- STATE \----------------"  
    \- id: REQ-5.1.6  
      text: Validate follow-up dates to be in the future and within one year.  
      rationale: Ensures valid and actionable follow-up scheduling.  
      source\_citations:  
        \- "\[5\] function validateFollowUp"  
    \- id: REQ-5.1.7  
      text: Maintain an activityLog with timestamps, actions, and prospect IDs, trimmed to 100 entries.  
      rationale: Provides a recent history of user and system interactions.  
      source\_citations:  
        \- "\[5\] function logActivity"  
    \- id: REQ-5.1.8  
      text: The Dashboard should display a "I Fokus" card with prospect name, status, temperature, and next follow-up, and an "Åpne kundekort" button.  
      rationale: Highlights key prospects and provides quick access to their details.  
      source\_citations:  
        \- "\[5\] function renderDashboard"  
    \- id: REQ-5.1.9  
      text: The Pipeline view should display a table of prospects with name, status, and temperature, with click functionality to open the prospect card.  
      rationale: Provides an overview of the sales pipeline and access to prospect details.  
      source\_citations:  
        \- "\[5\] function renderPipeline"  
    \- id: REQ-5.1.10  
      text: The Activity Log should display a list of logged activities with timestamps and actions.  
      rationale: Provides a clear record of system and user activities.  
      source\_citations:  
        \- "\[5\] function renderLogg"  
    \- id: REQ-5.1.11  
      text: The Prospect Card modal should display prospect name, status, temperature, a textarea for notes, an input for next follow-up date, and save/close buttons.  
      rationale: Provides a comprehensive and interactive view of prospect details.  
      source\_citations:  
        \- "\[5\] function renderModalCard"  
    \- id: REQ-5.1.12  
      text: Phase 2 Goal: Rebuild pipeline to follow Frazer Brookes’ recruiting flow: Conversations (Nytt Lead, Relationship Building) \-\> Invitations (Invited, Qualified) \-\> Presentations & Continuations (Presentation Sent, Follow-Up) \-\> Launch (Team Member).  
      rationale: Aligns the system with a proven recruiting methodology.  
      source\_citations:  
        \- "\[5\] 🎯 Mål med Phase 2; 🧩 Pipeline-steg (Frazer-metoden)"  
    \- id: REQ-5.1.13  
      text: Update Kundekort with a "Prospect's Why" field (from qualification).  
      rationale: Captures critical information for prospect engagement.  
      source\_citations:  
        \- "\[5\] 🛠️ Endringer vi gjør i systemet"  
    \- id: REQ-5.1.14  
      text: Dashboard's Next Best Action logic should be updated to be based on the new Frazer pipeline flow.  
      rationale: Ensures AI suggestions are aligned with the updated sales process.  
      source\_citations:  
        \- "\[5\]"

  non\_functional:  
    \- id: NFR-1.1.1  
      text: The system should emphasize consistent daily action over sporadic effort.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[1\] ALL IN ONE"  
    \- id: NFR-1.1.2  
      text: Conversations should be friendly, genuine, and focus on building rapport.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[1\] Section 1, NUMBER TWO"  
    \- id: NFR-1.1.3  
      text: The system should support a positive mindset and address internal roadblocks like fear of failure.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[1\] Section 4, NUMBER TWO"  
    \- id: NFR-2.1.1  
      text: Maintain a strong focus on problem-solving and fixing/modifying within the project's defined scope.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[2\] HOVEDREGLER PROMPT, \*"  
    \- id: NFR-2.1.2  
      text: The system should be robust, self-evolving, idiot-proof, elegant, scalable, and future-ready.  
      performance: Scalability is a key aspect.  
      security: Not specified  
      privacy: Not specified  
      reliability: Robustness and idiot-proof design contribute to reliability.  
      source\_citations:  
        \- "\[2\] dev// PROD DESCRIPTION:🌐Flowstate-AI, Iterative Process"  
    \- id: NFR-3.1.1  
      text: All important information (marked with bold text) should be given extra consideration.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[3\] B: Grunnleggende Prinsipper"  
    \- id: NFR-4.1.1  
      text: The CRM system should be beginner-friendly.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[4\] Core CRM System"  
    \- id: NFR-4.1.2  
      text: The CRM system should integrate into a larger affiliate marketing project.  
      performance: Not specified  
      security: Not specified  
      privacy: Not specified  
      reliability: Not specified  
      source\_citations:  
        \- "\[4\] Execution & AI Guidelines"  
    \- id: NFR-4.1.3  
      text: Interoperability, team workflows, and data handling (CSV imports 500–1,000+) are critical.  
      performance: Efficient handling of large CSV imports.  
      security: Not specified  
      privacy: Not specified  
      reliability: Interoperability and robust data handling.  
      source\_citations:  
        \- "\[4\] Execution & AI Guidelines"

constraints\_assumptions:  
  \- id: ASM-1.1.1  
    text: Users will track their progress based on activity rather than just results.  
    source\_citations:  
      \- "\[1\] Section 2"  
  \- id: ASM-2.1.1  
    text: The user (owner) will explicitly approve all automated code execution and file modifications.  
    source\_citations:  
      \- "\[2\] SVAR FRA COPILOT"  
  \- id: ASM-3.1.1  
    text: The original text's intent and content are preserved.  
    source\_citations:  
      \- "\[3\] Redaktørens Prosesslogg"  
  \- id: ASM-4.1.1  
    text: The uploaded MD file serves as a guide and instruction set for assembling the final CRM system.  
    source\_citations:  
      \- "\[4\] Code GPT sa, Here’s what’s clear now"

decisions:  
  \- id: DEC-2.1.1  
    status: accepted  
    text: Automatiseringens ansvar: CI/CD-pipelines håndterer bygg, tester og deploy. Assistenten kan opprette pipelines og skript, men kjøring skjer i CI (GitHub Actions) eller manuelt av deg.  
    rationale: Defines the responsibilities for automation and execution.  
    source\_citations:  
      \- "\[2\] SVAR FRA COPILOT"  
  \- id: DEC-3.1.1  
    status: accepted  
    text: Specific software brand names (Airtable, Make, Zapier, etc.) are to be downplayed or removed to focus on function, not specific implementation.  
    rationale: Ensures focus on core functionality and avoids vendor lock-in.  
    source\_citations:  
      \- "\[3\] Redaktørens Prosesslogg; B: Grunnleggende Prinsipper"  
  \- id: DEC-4.1.1  
    status: accepted  
    text: The user prioritizes a unified Master Build File over smaller connected files for modular use.  
    rationale: Streamlines documentation and provides a single source of truth.  
    source\_citations:  
      \- "\[4\] Du sa: A"  
  \- id: DEC-4.1.2  
    status: accepted  
    text: The user wants to refine/improve specific modules (AI scoring, automation, onboarding, gamification, etc.) rather than immediately proceeding with implementation code or an Airtable setup.  
    rationale: Focuses on iterative improvement and strategic development.  
    source\_citations:  
      \- "\[4\] Du sa: refine/improve specific modules"  
  \- id: DEC-4.1.3  
    status: accepted  
    text: The user prioritizes a "plug & play" CRM setup with minimal work.  
    rationale: Addresses user's need for ease of use and quick setup.  
    source\_citations:  
      \- "\[4\] Du sa: I don’t want to have lot of work; Minimal Work Strategy"  
  \- id: DEC-4.1.4  
    status: accepted  
    text: The user wants to understand the cost and skillset differences between Airtable (no-code) and a custom app (React \+ Backend).  
    rationale: Informs strategic decisions regarding technology stack and development approach.  
    source\_citations:  
      \- "\[4\] Du sa: What will cost money and does it last option require any skillsett? Or alot of other platforms?"

open\_questions:  
  \- id: Q-3.1.1  
    text: How can built-in AI (without external API costs initially) be implemented and what are alternative solutions?  
    source\_citations:  
      \- "\[3\] B: Grunnleggende Prinsipper"  
  \- id: Q-C-GAP-1  
    text: Detailed specifications for the self-evolving AI improvement loop are not fully elaborated.  
    source\_citations:  
      \- "\[2\] Documentation Standards" \# This citation is inferred from the context of TASK-2.1.2 and TASK-2.1.4, which relate to documenting AI evolution and improvements.  
      \- "\[5\] 🎯 Mål med Phase 2" \# This citation is inferred from Phase 3 goal of deepening AI capabilities and self-evolving loop.  
  \- id: Q-C-GAP-2  
    text: Concrete metrics or acceptance criteria for NFRs like "beginner-friendly", "elegant", "scalable", and "future-ready" are not provided.  
    source\_citations:  
      \- "\[2\] dev// PROD DESCRIPTION:🌐Flowstate-AI, Iterative Process" \# NFR-2.1.2 is here.  
      \- "\[4\] Core CRM System" \# NFR-4.1.1 is here.  
  \- id: Q-C-GAP-3  
    text: The specific identities of the "3 documents" for AI information gathering are not provided.  
    source\_citations:  
      \- "\[3\] Description of end product" \# REQ-3.1.1 is here.  
  \- id: Q-C-GAP-4  
    text: The process for "AI learning from user's tone/style" lacks specific implementation details.  
    source\_citations:  
      \- "\[3\] 5\. AI Follow-up assistent" \# REQ-3.1.13 is here.  
  \- id: Q-C-GAP-5  
    text: "REDBULL-PR" command and admin-override policy lack full detail on governance and process.  
    source\_citations:  
      \- "\[2\] REDBULL — admin-override policy" \# REQ-2.1.8 is here.  
  \- id: Q-C-GAP-6  
    text: The precise definition and calculation of "Relation-Score" and "Interest-Score" are not detailed.  
    source\_citations:  
      \- "\[3\] C.4: Databasen (\\"Prospect Hub\\")" \# REQ-3.1.7 is here.  
      \- "\[3\] 3\. Kundekort (klikk på navn → popup)" \# REQ-3.1.11 is here.  
  \- id: Q-C-GAP-7  
    text: "Next Best Action" logic for each pipeline stage is not fully laid out for the entire Frazer flow.  
    source\_citations:  
      \- "\[5\] 🎯 Mål med Phase 2; 🧩 Pipeline-steg (Frazer-metoden)" \# REQ-5.1.12 is here.  
      \- "\[5\]" \# REQ-5.1.14 is here.

risks:  
  \- id: RISK-2.1.1  
    text: Automatic code execution and file modifications without explicit approval could lead to unintended consequences.  
    mitigations: Explicit human approval processes.  
    source\_citations:  
      \- "\[2\] SVAR FRA COPILOT, Kort og tydelig"

entities\_data:  
  glossary:  
    \- term: CRM  
      definition: Customer Relationship Management  
    \- term: DMO  
      definition: Daily Method of Operation  
    \- term: IPA  
      definition: Income Producing Activity  
    \- term: CI/CD  
      definition: Continuous Integration/Continuous Deployment  
    \- term: PR  
      definition: Pull Request  
    \- term: NFR  
      definition: Non-Functional Requirement  
    \- term: REQ  
      definition: Requirement  
    \- term: ASM  
      definition: Assumption  
    \- term: DEC  
      definition: Decision  
    \- term: Q  
      definition: Open Question  
    \- term: RISK  
      definition: Risk  
    \- term: TASK  
      definition: Task  
    \- term: Kundekort  
      definition: Prospect Card (Norwegian)  
    \- term: Prospect Hub  
      definition: Database for prospect information  
    \- term: Action-Board  
      definition: Dashboard for user interaction  
  objects:  
    \- name: Prospect  
      attributes:  
        \- Name  
        \- Platform  
        \- Status  
        \- Next Step  
        \- Notes  
        \- Prospect-ID (auto-generated)  
        \- Contact Channel  
        \- Relation Level (AI-calculated 1-5)  
        \- AI-score (e.g., "Probability to book introcall \= 73%")  
        \- Prospect's Why (from qualification)  
        \- Relation-Score (AI-generated)  
        \- Interest-Score (AI-generated)  
      relationships:  
        \- Has many Activities  
        \- Belongs to a Pipeline Stage  
    \- name: Activity  
      attributes:  
        \- Timestamp  
        \- Action  
        \- Prospect ID  
    \- name: Follow-up  
      attributes:  
        \- Date  
        \- Status  
        \- Message Suggestions (AI-generated)  
    \- name: Meeting  
      attributes:  
        \- Title (AI-recognized)  
        \- Status (No-show, Gjennomført)  
        \- Date  
    \- name: User  
      attributes:  
        \- Tone/Style (for AI learning)  
    \- name: System  
      attributes:  
        \- AppData (saved to localStorage)  
        \- Rules (in RULES.md)  
        \- System Design Notes  
        \- Process Reports  
        \- Improvement Logs  
        \- Blueprints  
        \- Master Build File  
  attributes:  
    \- Name  
    \- Platform  
    \- Status  
    \- Next Step  
    \- Notes  
    \- Category (REQ, NFR, ASM, TASK, DEC, RISK, Q)  
    \- ID  
    \- Description  
    \- Source  
    \- Status (Stable, Not specified)  
    \- Creation Succeeded  
    \- Error Details  
    \- File  
    \- Parent Folder  
    \- Title  
    \- URL  
    \- Move Results  
    \- Move Succeeded  
    \- Result Summary  
    \- Action Status  
    \- Saved Gmail Attachment Data  
    \- File ID  
    \- Message ID  
    \- Part ID  
    \- Query  
    \- Corpus  
    \- Search Query  
    \- Kind  
    \- Summarized Content  
    \- Query Interpretation  
    \- Destination Folder  
    \- Move Status  
    \- Source Folder  
    \- File Type  
    \- Parent Folder ID  
  relationships: Not specified

workflows\_processes:  
  \- name: Frazer Brookes Recruiting Flow (Phase 2 Goal)  
    stages:  
      \- Conversations (Nytt Lead, Relationship Building)  
      \- Invitations (Invited, Qualified)  
      \- Presentations & Continuations (Presentation Sent, Follow-Up)  
      \- Launch (Team Member)  
    triggers: Not specified  
    inputs\_outputs: Not specified  
    source\_citations:  
      \- "\[5\] 🎯 Mål med Phase 2; 🧩 Pipeline-steg (Frazer-metoden)"  
  \- name: Data Flow  
    stages:  
      \- User Input (UI interaction to add prospects, log activities, update statuses, schedule follow-ups)  
      \- Data Storage (Input saved to Prospect Hub)  
      \- AI Processing (AI Engine analyzes data to update scores, generate "Next Best Actions," trigger automated tasks, refine learning)  
      \- Output to UI (Processed info, AI suggestions, automated tasks displayed on Dashboard, Kundekort, notifications)  
      \- External Integrations (Calendar events synced with Google Calendar, CSV data

