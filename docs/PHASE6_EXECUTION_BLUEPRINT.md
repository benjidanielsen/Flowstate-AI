# GODMODE Launch Execution Blueprint

_This document supersedes the old Phase 6 notes. The filename remains for
backwards compatibility, but the content now explains how to run the nine-hour
GODMODE Brain launch sequence end-to-end._

## 1. Mission Overview

**Objective:** Activate the GODMODE Brain, unleash the autonomous build army on
the Flowstate-AI CRM, and graduate to a live pilot with five human operators –
all inside a nine-hour runway.

**Timeboxes:** Three phases, each fixed at three hours.

| Phase | Window | Theme |
| --- | --- | --- |
| `phase_1_ai_brain` | Hours 0-3 | Assemble the coordination brain and publish the command board. |
| `phase_2_crm_delivery` | Hours 3-6 | Execute the CRM build sprints with autonomous squads. |
| `phase_3_launch` | Hours 6-9 | Stage the live pilot, train operators, and issue the go/no-go call. |

**Key Artefacts:**
- `collective-memory/godmode_brain_plan.json` – canonical machine-readable plan.
- `collective-memory/project_status.json` – status ledger updated via
  `godmode_brain.py`.
- `docs/GODMODE_BRAIN_ROADMAP.md` – human-readable overview.
- `docs/launch/FINAL_LAUNCH_CHECKLIST.md` – timeboxed deliverables + readiness gates.
- `AUTONOMOUS_WORK_LOG.md` – claim/complete task board (mandatory rule).

## 2. Pre-Flight Checklist

| Item | Command / Action | Notes |
| --- | --- | --- |
| Python toolchain | `pyenv local 3.11.9` (or ensure Python ≥ 3.11) | Supports orchestrator + agent stack. |
| Node.js backend | `nvm use 18` | Matches backend/services requirements. |
| Dependencies | `npm run setup` and `pip install -r python-worker/requirements.txt` | Installs CRM + automation deps. |
| Redis (optional) | `redis-server` | Enables real-time comms when available; orchestrator handles fallback. |
| Database | `npm run db:migrate && npm run db:seed` | Seeds CRM data for demos/tests. |
| Logging dirs | auto-provisioned | `load_project_manager_config` creates paths on demand. |

## 3. Phase Playbooks

### Phase 1 – Assemble the GODMODE Brain (0h → 3h)

| Step | Description | Output |
| --- | --- | --- |
| `p1_s1` | Load `project_manager_enhanced.py`, `communication_hub_enhanced.py`, and `error_handling.py` with shared config to verify coordination wiring. | Successful health check logs and updated config references. |
| `p1_s2` | Translate MACCS-era messaging principles into the collective memory + communication schemas. | Knowledge base entries + routing tables derived from Manus lessons. |
| `p1_s3` | Publish the roadmap (`docs/GODMODE_BRAIN_ROADMAP.md`), JSON plan, and task board updates. | Signed work log entries and roadmap links shared with the team. |

**Validation:**
- `python ai-gods/project_manager_enhanced.py --health-check`
- `python ai-gods/godmode_brain.py --show-plan`
- Work log entries updated with owners + deliverables.

### Phase 2 – Mobilise the AI Build Army (3h → 6h)

| Step | Description | Output |
| --- | --- | --- |
| `p2_s1` | Register specialised squads via the Project Manager AI (`create_task` + capability mapping). | Agent roster + seeded task queues. |
| `p2_s2` | Enable automated test/review chains (`python -m unittest`, `npm test`, lint hooks). | Passing pipelines with logs stored under `godmode-logs/`. |
| `p2_s3` | Run integrated CRM demos; capture telemetry and defect tickets in the command board. | Demo recordings, telemetry exports, and prioritised defect backlog. |

**Validation:**
- `python ai-gods/project_manager_enhanced.py --demo`
- `python -m unittest discover -s tests`
- `npm test`

### Phase 3 – Stage the Live Pilot (6h → 9h)

| Step | Description | Output |
| --- | --- | --- |
| `p3_s1` | Prepare deployment artefacts, secrets, and rollback playbooks. | Deployment runbook + automated health checks. |
| `p3_s2` | Deliver operator onboarding kits, sandbox sessions, and access provisioning. | Signed access forms + quick-start guides for five operators. |
| `p3_s3` | Execute the acceptance window, collect feedback, and record the launch decision. | Launch decision record + backlog of follow-up actions. |

**Validation:**
- `python ai-gods/godmode_brain.py --set-phase phase_3_launch --mark-complete phase_1_ai_brain phase_2_crm_delivery`
- Staging smoke tests executed (document results in work log).
- Operator sign-off attachments stored in `collective-memory/`.

## 4. Reporting Cadence

1. Update the work log at phase boundaries (start, mid-phase, completion).
2. Attach log excerpts, demo recordings, and decision notes in the Notes column.
3. When advancing phases, run `python ai-gods/godmode_brain.py --set-phase <key>
   --mark-complete <completed>` to keep the status ledger authoritative.

## 5. Escalation Paths

- **Blocking Dependencies:** Document blockers in the work log and escalate via
  the communication hub broadcast channel.
- **Environment Failures:** Trigger `ai-gods/autonomous_development.py` self-
  healing routines or file a task under `p1_s1` if wiring regresses.
- **Scope Drift:** Use the voting workflow inside `project_manager_enhanced.py`
  to approve adjustments before execution.

## 6. Change Log

| Date | Update |
| --- | --- |
| 2025-10-03 | Replaced Phase 6 content with the GODMODE launch blueprint and linked roadmap/status artefacts. |
