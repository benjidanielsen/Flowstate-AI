```yaml
---
title: Affiliate Network Marketing CRM - AI Execution and Project Guidelines
purpose: Complements NWM_CRM_Complete_System.md with project context, operational guidelines, and AI execution notes for integrating the CRM into a larger affiliate network marketing project.
usage: Use with NWM_CRM_Complete_System.md to guide AIs in project prompt development and CRM integration, and team members in operational planning. Copy to project folder and export to PDF.
project_context: Part of a larger affiliate network marketing project; ensures CRM alignment with broader goals while preserving all features (e.g., AI automation, Activo-style Dashboard).
created: 2025-08-29
intended_audience: AIs for prompt development and execution, team members for operational planning
related_file: NWM_CRM_Complete_System.md
---
```

# Affiliate Network Marketing CRM: AI Execution and Project Guidelines

This file complements `NWM_CRM_Complete_System.md`, which defines the CRM system’s core description, three AI-driven implementation plans, and usage instructions, finalized on 2025-08-29. This file provides broader project context, operational guidelines, and AI execution notes to integrate the CRM into a larger affiliate network marketing project, ensuring all CRM features (e.g., beginner-friendly, AI-driven automation, Activo-style Dashboard, 20 new prospects + 30 follow-ups, GDPR compliance) are preserved while allowing flexibility for other project components (e.g., marketing funnels, analytics). Both files form a complete package, with explicit links to ensure logical comprehension and easy implementation. Copy as `NWM_CRM_AI_and_Project_Guidelines.md` and export to `.pdf`.

## Relationship Between Files
- **NWM_CRM_Complete_System.md**: Primary reference with CRM principles, components (Prospects, Dashboard, Improvements), and three free implementations (HubSpot, EngageBay, Google Sheets) with backtested results (26-29% conversions).
- **NWM_CRM_AI_and_Project_Guidelines.md**: Provides project context (e.g., CRM as a module), operational guidelines (team workflows, data management), and AI execution notes for integration without limiting broader project scope.
- **Usage**: Use both files together. AIs should parse `NWM_CRM_Complete_System.md` for CRM specs and this file for project integration. Teams should review both (or PDFs) for planning and execution.

## Project Context
- **Scope**: The CRM is a module within a larger affiliate network marketing project, potentially including marketing funnels, analytics dashboards, or affiliate tracking. It manages prospect relationships, feeding data (e.g., lead scores, conversion reports) to other modules.
- **Goals**: Maximize affiliate recruitment/sales via automated prospect management, supporting 1-15 users initially with scalability for growth (e.g., 1,000+ contacts).
- **Flexibility**: Platforms (e.g., HubSpot) are examples; AIs can choose alternatives (e.g., custom databases, Notion) if CRM features remain unchanged.

## Operational Guidelines
- **Team Collaboration**:
  - **Roles**: Assign members to input prospects (via forms), monitor Dashboard (ticker, “Neste kundekort”), and review AI coaching (4-6 daily questions).
  - **Workflow**: Daily: enter 20 prospects + 30 follow-ups, check IPA (60-120 min), log improvements. Weekly: review AI reports/graphs.
  - **Tools**: Use free collaboration tools (e.g., Google Workspace, Slack free tier) to share CRM outputs (e.g., PDF reports).
- **Data Management**:
  - **Imports**: Support CSV imports (500-1,000+ prospects) with standardized templates (e.g., Navn, Plattform).
  - **GDPR**: Enforce opt-in consent, disclaimers, 5-year dead lead retention via AI automation.
  - **Backups**: Export CRM data weekly to Google Drive.
- **Training**: Use 5-10 min tutorials (e.g., HubSpot wiki, support.google.com) for no-tech setup/use.

## AI Execution Notes
- **Parsing**: Read YAML metadata and sections of both files. Use `<xaiArtifact>` tags for xAI compatibility.
- **Prioritization**: Focus on AI-driven automation (scoring, follow-ups, coaching) and Activo-style Dashboard (pop-up kundekort, 10-second ticker) from `NWM_CRM_Complete_System.md`.
- **Integration**: Connect CRM to project components (e.g., email marketing, analytics) via no-code connectors (e.g., Zapier free tier, Google Calendar API). Ensure data flow (e.g., lead scores to dashboards).
- **Testing**: Simulate flows (add 20 prospects, mark no-show, check ticker) to match backtested 26-29% conversions, 7-9% missed follow-ups.
- **Scalability**: Design for growth (e.g., 1,000+ contacts) and extend functionality for other modules (e.g., affiliate payouts) without altering CRM features.
- **Error Handling**: If platform limits (e.g., EngageBay’s 250 contacts) are restrictive, propose alternatives with feature parity.
- **Prompt Development**: Build a project prompt using both files, preserving CRM features while supporting broader project goals.

## Instructions for Use
1. **Copy to Project**: Save as `NWM_CRM_AI_and_Project_Guidelines.md` in your project folder (e.g., `/project/crm_docs/`).
2. **Export to PDF**: Open in Typora/Obsidian and export via “Print to PDF,” or use `pandoc NWM_CRM_AI_and_Project_Guidelines.md -o NWM_CRM_AI_and_Project_Guidelines.pdf`.
3. **AI Processing**: Parse YAML metadata and sections with `NWM_CRM_Complete_System.md` for CRM specs and this file for project integration.
4. **Team Use**: Share PDF, pointing to this section. Use with `NWM_CRM_Complete_System.md` for full context.
5. **Notes**: Both files are interdependent; platforms are flexible, but CRM features must remain unchanged. Setups are no-tech, verified by 2025 G2/TechRadar reviews.