# Frontend - Flowstate-AI

## Forthcoming Structure
The refreshed repository will reshape the frontend into feature-driven workspaces while maintaining Vite as the build tool. Planned top-level folders include:

- `app/` – Entry shell, routing, global providers, and layout scaffolding.
- `features/` – End-to-end verticals for CRM dashboards, AI oversight, customer records, and KPI analytics.
- `design-system/` – Shared components, tokens, and Tailwind configuration primitives.
- `data-access/` – API clients, query hooks, and caching adapters shared across features.
- `testing/` – Vitest utilities, Storybook scenarios, and accessibility checks.
- `tooling/` – ESLint configs, Vite plugins, and code-generation scripts.

Until the migration completes, legacy code remains under `src/`. Use this README to align new work with the destination layout and to flag refactors during planning discussions.

## Day-to-Day Workflow
- Install dependencies from the project root or from `frontend/` with `npm install`.
- Start the development server via `npm run dev` (proxied through the root `npm run dev:frontend`).
- Run unit and component tests with `npm run test` and launch the Vitest UI using `npm run test:ui` when iterating on components.

## Migration Callouts
- Shared contexts (`AuthContext`, `ToastContext`) will relocate to `app/providers/` when the restructure lands.
- The axios instance and typed service wrappers will consolidate into `data-access/clients/`.
- Component-level styles should graduate into `design-system/` as Tailwind primitives replace ad-hoc CSS modules.
