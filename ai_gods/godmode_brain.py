"""GODMODE Brain orchestrator.

This module coordinates the three-hour launch sequence for the FlowState-AI
GODMODE initiative.  It consolidates the historical GODMODE planning documents
into a single, reproducible plan that can be executed by autonomous agents or
human operators.  The orchestrator stores the canonical plan alongside the
project status file so the roadmap is visible to everyone collaborating on the
repository.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from ai_gods.project_manager_config import ProjectManagerConfig, load_project_manager_config


@dataclass
class PhaseStep:
    """Represents an actionable unit of work within a phase."""

    key: str
    name: str
    summary: str
    owner: str
    duration_minutes: int
    deliverables: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)


@dataclass
class PhasePlan:
    """Represents a launch phase within the GODMODE roadmap."""

    key: str
    title: str
    objective: str
    timebox_hours: int
    narrative: str
    dependencies: List[str] = field(default_factory=list)
    steps: List[PhaseStep] = field(default_factory=list)

    def as_dict(self) -> Dict[str, object]:
        return {
            "key": self.key,
            "title": self.title,
            "objective": self.objective,
            "timebox_hours": self.timebox_hours,
            "narrative": self.narrative,
            "dependencies": self.dependencies,
            "steps": [asdict(step) for step in self.steps],
        }


class GodmodeBrain:
    """Central coordinator for the GODMODE launch roadmap."""

    def __init__(
        self,
        config: Optional[ProjectManagerConfig] = None,
        plan_path: Optional[Path] = None,
        status_path: Optional[Path] = None,
    ) -> None:
        self.config = config or load_project_manager_config()
        self.plan_path = (
            Path(plan_path)
            if plan_path
            else Path("collective-memory/godmode_brain_plan.json")
        )
        self.status_path = (
            Path(status_path)
            if status_path
            else Path("collective-memory/project_status.json")
        )
        self.plan_path.parent.mkdir(parents=True, exist_ok=True)
        self.status_path.parent.mkdir(parents=True, exist_ok=True)
        self.plan = self._load_or_create_plan()

    # ------------------------------------------------------------------
    # Plan generation
    # ------------------------------------------------------------------
    def _load_or_create_plan(self) -> Dict[str, object]:
        if self.plan_path.exists():
            with self.plan_path.open("r", encoding="utf-8") as handle:
                return json.load(handle)

        plan = self._generate_plan()
        self.persist_plan(plan)
        return plan

    def _generate_plan(self) -> Dict[str, object]:
        """Create the canonical three-phase roadmap."""

        phases = [
            PhasePlan(
                key="phase_1_ai_brain",
                title="Assemble the GODMODE Brain",
                objective="Stabilise and wire together the autonomous coordination core",
                timebox_hours=3,
                narrative=(
                    "Bootstrap the living brain of the platform by consolidating project manager, "
                    "communication hub, and continuous improvement capabilities into a single "
                    "operational heartbeat."
                ),
                steps=[
                    PhaseStep(
                        key="setup_vscode_environment",
                        name="Setup VS Code Environment",
                        summary="Ensure all required VS Code extensions are installed and the environment is correctly configured.",
                        owner="VSCodeAgent",
                        duration_minutes=10,
                        deliverables=["A fully configured VS Code environment"],
                    ),
                    PhaseStep(
                        key="autofix_workspace",
                        name="Run Autofix on Entire Workspace",
                        summary="Trigger the new autofixer agent to perform a full scan and repair cycle on the entire codebase to establish a clean baseline.",
                        owner="FixerAI",
                        duration_minutes=30,
                        deliverables=["A clean and error-free codebase baseline"],
                        dependencies=["setup_vscode_environment"],
                    ),
                    PhaseStep(
                        key="consolidate_pm",
                        name="Consolidate Project Management",
                        summary="Merge the legacy project management scripts into a unified project manager agent.",
                        owner="ProjectManagerAgent",
                        duration_minutes=60,
                        deliverables=["A single, authoritative project manager agent"],
                        dependencies=["autofix_workspace"],
                    ),
                    PhaseStep(
                        key="p1_s1",
                        name="Unify coordination stack",
                        summary=(
                            "Load the enhanced project manager, error handling, and communication hub "
                            "modules with shared configuration so the brain starts with battle-tested "
                            "foundations."
                        ),
                        owner="architecture",
                        duration_minutes=60,
                        deliverables=[
                            "Validated configuration wiring",
                            "Shared logging + retry primitives applied",
                        ],
                    ),
                    PhaseStep(
                        key="p1_s2",
                        name="Codify knowledge architecture",
                        summary=(
                            "Inject legacy Manus lessons (asynchronous messaging, durable decision logs, "
                            "and expertise routing) into the collective memory model."
                        ),
                        owner="collective_intelligence",
                        duration_minutes=55,
                        deliverables=[
                            "Updated collective-memory schemas",
                            "Reference plan mapping Manus MACCS mechanisms to GODMODE equivalents",
                        ],
                    ),
                    PhaseStep(
                        key="p1_s3",
                        name="Publish master command board",
                        summary=(
                            "Materialise the GODMODE roadmap in docs, JSON, and status dashboards so every "
                            "participant can see and claim work in one glance."
                        ),
                        owner="program_management",
                        duration_minutes=65,
                        deliverables=[
                            "Godmode brain roadmap published",
                            "Updated work log + status JSON",
                        ],
                    ),
                    PhaseStep(
                        key="commit_and_push_plan",
                        name="Commit and Push Plan",
                        summary="Commit the generated GODMODE plan to the repository and push it to the remote.",
                        owner="GitAgent",
                        duration_minutes=5,
                        deliverables=[
                            "The GODMODE plan committed and pushed to the remote repository"
                        ],
                        dependencies=["p1_s3"],
                    ),
                ],
            ),
            PhasePlan(
                key="phase_2_crm_delivery",
                title="Mobilise the AI build army",
                objective="Drive autonomous feature delivery for the Flowstate-AI CRM",
                timebox_hours=3,
                narrative=(
                    "With the brain online, swarm the CRM backlog with specialised AI contributors, "
                    "leveraging question routing and quality gates to finish the core product."
                ),
                dependencies=["phase_1_ai_brain"],
                steps=[
                    PhaseStep(
                        key="p2_s1",
                        name="Spin up specialised squads",
                        summary=(
                            "Instantiate backend, frontend, automation, and data squads through the project "
                            "manager interface with clear acceptance criteria."
                        ),
                        owner="project_manager_ai",
                        duration_minutes=45,
                        deliverables=[
                            "Squad definitions + capabilities registered",
                            "Task queues seeded from CRM backlog",
                        ],
                        dependencies=["p1_s1"],
                    ),
                    PhaseStep(
                        key="p2_s2",
                        name="Automate continuous build & review",
                        summary=(
                            "Enable design-to-deploy loops with automated testing, code review hand-offs, "
                            "and quality enforcement using the collective memory playbooks."
                        ),
                        owner="devops",
                        duration_minutes=60,
                        deliverables=[
                            "Automated regression + lint suites configured",
                            "Decision + fix logs attached to knowledge base",
                        ],
                    ),
                    PhaseStep(
                        key="p2_s3",
                        name="Battle-test CRM verticals",
                        summary=(
                            "Run integrated demos for sales pipeline, communications, and analytics flows, "
                            "logging defects directly into the autonomous backlog."
                        ),
                        owner="quality_engineering",
                        duration_minutes=75,
                        deliverables=[
                            "Demo scripts + telemetry reports",
                            "Prioritised defect tickets with owners",
                        ],
                    ),
                ],
            ),
            PhasePlan(
                key="phase_3_launch",
                title="Stage live pilot",
                objective="Prepare production launch with five human operators",
                timebox_hours=3,
                narrative=(
                    "Coordinate human acceptance, live environment readiness, and observability so the "
                    "system ships confidently within the nine-hour window."
                ),
                dependencies=["phase_2_crm_delivery"],
                steps=[
                    PhaseStep(
                        key="p3_s1",
                        name="Pilot environment hardening",
                        summary=(
                            "Provision staging + production configs, integrate secure secrets, and run "
                            "smoke tests mirroring the pilot setup."
                        ),
                        owner="site_reliability",
                        duration_minutes=55,
                        deliverables=[
                            "Deployment runbooks",
                            "Automated health + rollback routines",
                        ],
                        dependencies=["p2_s2"],
                    ),
                    PhaseStep(
                        key="p3_s2",
                        name="Human operator onboarding",
                        summary=(
                            "Deliver concise operator guides, access packages, and sandbox walkthroughs for "
                            "the five pilot users."
                        ),
                        owner="enablement",
                        duration_minutes=50,
                        deliverables=[
                            "Pilot access packets",
                            "Feedback capture templates",
                        ],
                    ),
                    PhaseStep(
                        key="p3_s3",
                        name="Final triage + go/no-go",
                        summary=(
                            "Execute the three-hour acceptance window, collect findings, and document the "
                            "launch decision with sign-offs."
                        ),
                        owner="program_management",
                        duration_minutes=85,
                        deliverables=[
                            "Launch decision record",
                            "Backlog of follow-up improvements",
                        ],
                    ),
                ],
            ),
        ]

        return {
            "version": "2025.10-godmode-brain",
            "generated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "source_documents": {
                "analysis": "docs/godmode/AI_AGENT_ECOSYSTEM_ANALYSIS_V2.md",
                "system_design": "docs/godmode/GODMODE_AI_AGENT_SYSTEM_DOCUMENTATION_V2.md",
                "enhancements": "docs/godmode/GODMODE_AI_AGENT_ENHANCEMENTS_DOCUMENTATION.md",
                "original_plan": "docs/godmode/GODMODE_AI_AGENT_PLAN.md",
            },
            "execution_principles": [
                "Every task claimed, executed, and reported through the published command board.",
                "Redis + SQLite wiring are optional but prepared so autonomous agents can scale instantly.",
                "Legacy Manus MACCS insights preserved via asynchronous messaging patterns and durable logs.",
            ],
            "phases": [phase.as_dict() for phase in phases],
        }

    # ------------------------------------------------------------------
    # Persistence helpers
    # ------------------------------------------------------------------
    def persist_plan(self, plan: Optional[Dict[str, object]] = None) -> None:
        data = plan or self.plan
        with self.plan_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    # ------------------------------------------------------------------
    # Status synchronisation
    # ------------------------------------------------------------------
    def update_status(
        self,
        current_phase: Optional[str] = None,
        completed_phases: Optional[List[str]] = None,
        notes: Optional[str] = None,
    ) -> Dict[str, object]:
        completed_phases = completed_phases or []
        current_phase = (
            current_phase or completed_phases[-1]
            if completed_phases
            else self.plan["phases"][0]["key"]
        )
        phase_order = [phase["key"] for phase in self.plan["phases"]]

        status_payload = {
            "current_phase": current_phase,
            "completed_phases": completed_phases,
            "phase_order": phase_order,
            "timeboxes_hours": {
                phase["key"]: phase["timebox_hours"] for phase in self.plan["phases"]
            },
            "system_status": (
                "READY_FOR_EXECUTION" if not completed_phases else "IN_PROGRESS"
            ),
            "ai_agents_active": 11,
            "notes": notes or "",
            "updated_at": datetime.utcnow().replace(microsecond=0).isoformat() + "Z",
            "next_milestone": self._compute_next_milestone(
                current_phase, completed_phases, phase_order
            ),
        }

        with self.status_path.open("w", encoding="utf-8") as handle:
            json.dump(status_payload, handle, indent=2)

        return status_payload

    def _compute_next_milestone(
        self, current_phase: str, completed: List[str], phase_order: List[str]
    ) -> Optional[str]:
        try:
            index = phase_order.index(current_phase)
        except ValueError:
            return None

        phase = self.plan["phases"][index]
        start_time = datetime.utcnow().replace(microsecond=0)
        duration = timedelta(hours=phase["timebox_hours"])
        return (start_time + duration).isoformat() + "Z"

    # ------------------------------------------------------------------
    # Query helpers
    # ------------------------------------------------------------------
    def get_phase(self, key: str) -> Optional[Dict[str, object]]:
        for phase in self.plan["phases"]:
            if phase["key"] == key:
                return phase
        return None

    def list_phase_keys(self) -> List[str]:
        return [phase["key"] for phase in self.plan["phases"]]

    def get_master_plan(self, goal: str) -> List[Dict[str, Any]]:
        return [
            {
                "task_id": "autofix_001",
                "description": "Initial System-Wide Autofix",
                "agent": "ProjectManagerAgent",
                "action": "autofix_request",
                "dependencies": [],
                "priority": "critical",
            },
            {
                "task_id": "task_001",
                "description": f"Deconstruct the goal: '{goal}'",
                "agent": "ProjectManagerAgent",
                "dependencies": ["autofix_001"],
                "priority": "high",
            },
            {
                "task_id": "task_002",
                "description": "Develop a detailed, step-by-step execution plan",
                "agent": "ProjectManagerAgent",
                "dependencies": ["task_001"],
                "priority": "high",
            },
            {
                "task_id": "task_003",
                "description": "Execute the plan, delegating tasks to specialized agents",
                "agent": "ProjectManagerAgent",
                "dependencies": ["task_002"],
                "priority": "medium",
            },
            {
                "task_id": "task_004",
                "description": "Continuously monitor progress and adapt the plan",
                "agent": "ProjectManagerAgent",
                "dependencies": ["task_003"],
                "priority": "medium",
            },
            {
                "task_id": "task_005",
                "description": "Final integration, testing, and validation",
                "agent": "ProjectManagerAgent",
                "dependencies": ["task_004"],
                "priority": "high",
            },
            {
                "task_id": "self_improve_001",
                "description": "Continuously look for opportunities to improve the system",
                "agent": "InnovationAI",
                "action": "proactive_self_improvement",
                "dependencies": ["task_005"],
                "priority": "low",
                "is_recurring": True,
            },
        ]

    def execute_plan(self, plan: List[Dict[str, Any]]):
        for task in plan:
            task_id = task["task_id"]
            description = task["description"]
            agent = task["agent"]
            action = task.get("action", "execute_task")
            dependencies = task.get("dependencies", [])
            priority = task.get("priority", "normal")
            is_recurring = task.get("is_recurring", False)

            # Here you would integrate with the actual task execution logic,
            # for example, sending the task to the specified agent for execution.
            print(
                f"Executing {action} for {description} (Task ID: {task_id}) "
                f"with dependencies: {dependencies}"
            )

            if is_recurring:
                print(
                    f"Task {task_id} is recurring. It will reappear in the backlog after completion."
                )

    # ------------------------------------------------------------------
    # CLI interface
    # ------------------------------------------------------------------
    def cli(self, args: Optional[List[str]] = None) -> None:
        parser = argparse.ArgumentParser(description="GODMODE Brain control interface")
        parser.add_argument(
            "--show-plan",
            action="store_true",
            help="Print the consolidated launch roadmap",
        )
        parser.add_argument(
            "--set-phase",
            choices=self.list_phase_keys(),
            help="Update the current phase",
        )
        parser.add_argument(
            "--mark-complete",
            nargs="*",
            choices=self.list_phase_keys(),
            help="Mark phases as completed",
        )
        parser.add_argument(
            "--notes", help="Optional status note to persist with the update"
        )
        parsed = parser.parse_args(args=args)

        if parsed.show_plan:
            print(json.dumps(self.plan, indent=2))

        if parsed.set_phase or parsed.mark_complete:
            completed = parsed.mark_complete or []
            status = self.update_status(parsed.set_phase, completed, parsed.notes)
            print(json.dumps(status, indent=2))


def main() -> None:
    brain = GodmodeBrain()
    brain.cli()


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    main()

 
