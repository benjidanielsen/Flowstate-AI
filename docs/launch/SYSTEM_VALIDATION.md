# GODMODE System Validation Runbook

The Flowstate-AI launch requires a fast, repeatable way to prove the AI brain,
CRM services, and automation helpers are healthy before inviting the pilot
operators. Use this runbook whenever you need to certify a branch, prepare a
release candidate, or troubleshoot regressions uncovered by the GODMODE brain.

## 1. Prerequisites

- Python 3.11+
- Node.js 18+
- Playwright browsers installed (`npx playwright install`)
- Redis/PostgreSQL if the target scenario depends on them (local development
  works with the in-repo SQLite defaults)
- A configured `.env` for the backend and python worker if you are testing
  integrations

## 2. One-Command Validation

Run the platform-specific script from the repository root:

```bash
scripts/unix/FULL_SYSTEM_CHECK.sh
```

On Windows PowerShell:

```powershell
./scripts/windows/FULL_SYSTEM_CHECK.ps1
```

Each script performs:

1. **Python compile validation** for the GODMODE automation modules.
2. **Unit tests** for resilience helpers, the configuration loader, and the
   GODMODE brain.
3. **Health checks & demo seeding** through `project_manager_enhanced.py`.
4. **Workspace linting and builds** for the Node.js services when `npm` is
   available.
5. **Optional Playwright smoke tests** when the CLI is installed.

Command-line flags:

- `./scripts/windows/FULL_SYSTEM_CHECK.ps1 -SkipNode` — Skip Node.js lint/build
  on machines without Node installed.
- `./scripts/windows/FULL_SYSTEM_CHECK.ps1 -SkipE2E` — Skip Playwright checks.

## 3. Manual Follow-Ups

If any step fails, record the outcome in `AUTONOMOUS_WORK_LOG.md` and assign the
remediation task to an available contributor. The GODMODE brain plan JSON is
updated automatically when you mark a launch phase complete.

For deeper debugging:

- `python ai-gods/godmode_brain.py --show-plan` — Inspect launch sequencing.
- `python ai-gods/project_manager_enhanced.py --run` — Start the coordination
  loop with live logging.
- `npm run dev` — Boot the frontend and backend for manual QA.

## 4. Ready-to-Launch Criteria

The system is considered launch-ready when:

- The full system check passes on at least one clean environment.
- Outstanding issues from the GODMODE launch checklist are closed or assigned
  with mitigation notes in the work log.
- The pilot access playbook (see `docs/launch/FINAL_LAUNCH_CHECKLIST.md`) has
  been executed through the hand-off stage.

Document the validation run in the work log and proceed to deployment.
