# Documentation Hub

## Planned Structure
Documentation is consolidating into a navigable knowledge base with the following pillars:

- `guides/` – Step-by-step onboarding, setup, and operational walk-throughs.
- `reference/` – API contracts, data dictionaries, and schema catalogs sourced from OpenAPI/Drizzle definitions.
- `runbooks/` – Incident response, deployment checklists, and recovery procedures.
- `architecture/` – System diagrams, capability maps, and decision records.
- `roadmap/` – Strategy notes, milestone planning, and change logs.
- `annex/` – Historical snapshots such as `current-state.md` and archived design artifacts.

Existing Markdown files stay at the root of `docs/` until they are migrated into their destination folders. Each new document should link back to this index so contributors can follow the evolving taxonomy.

## Immediate Actions
- Use `docs/current-state.md` as the baseline inventory when planning module migrations.
- Prefer adding new knowledge to the target sub-folders above, even if the content starts as a placeholder that will be expanded later.
- Coordinate with the automation team so doc generation jobs land outputs in `reference/` rather than polluting feature directories.
