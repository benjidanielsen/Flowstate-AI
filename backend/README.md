# Backend - Flowstate-AI

## Forthcoming Structure
As part of the repository refresh the backend will be organized around explicit service boundaries. The target layout is:

- `apps/api/` – Express entrypoints, HTTP adapters, and API composition glue.
- `modules/crm/` – Customer, interaction, reminder, and pipeline workflows.
- `modules/ai/` – Agent orchestration, vector search, and evolution orchestration bridges.
- `modules/analytics/` – KPI dashboards, reporting, and telemetry aggregation flows.
- `platform/` – Cross-cutting middleware, logging, tracing, and shared utilities.
- `infrastructure/` – Database adapters, Supabase integrations, Drizzle migrations, and SQL seeds.
- `tests/` – Contract, integration, and smoke suites run via Jest and Supertest.

Current TypeScript sources still live under `src/` until migration lands; use this README as the canonical map for where code will move during the re-architecture.

## Local Development
1. Install dependencies from the backend directory:
   ```bash
   cd backend
   npm install
   ```
2. Start the dev server (TypeScript watch mode):
   ```bash
   npm run dev
   ```
3. Run unit and integration tests with open-handle detection:
   ```bash
   npm run test -- --detectOpenHandles --runInBand
   ```

## Operational Notes
- The server exports `createApp()`, `startServer()`, and `shutdown()` from `src/index.ts` so automated tests can manage lifecycle without forcing `process.exit`.
- Running `node dist/index.js` attaches SIGINT/SIGTERM handlers that call `shutdown()` for graceful exits in production-like environments.
- Database migrations and seeds are surfaced through `npm run db:migrate` and `npm run db:seed`; these commands will relocate under `platform/` as the directory layout evolves.
