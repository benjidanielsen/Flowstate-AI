import json
import logging
import os
import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Literal, Callable, Awaitable
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3001")
from ai_gods.logging_config import setup_logging
from evolution_framework.self_modification_orchestrator import SelfModificationOrchestrator
from evolution_framework.evolution_governor import EvolutionGovernor
from evolution_framework.evolution_manager import FlowstateEvolutionManager
from evolution_framework.anomaly_detector import AnomalyDetector
from evolution_framework.metrics_collector import MetricsCollector
from evolution_framework.multi_agent_coordinator import MultiAgentCoordinator
from evolution_framework.human_oversight_manager import HumanOversightManager
from evolution_framework.performance_tuner import PerformanceTuner
from evolution_framework.cost_optimizer import CostOptimizer
from evolution_framework.config import EvolutionConfig
app = FastAPI(title="Flowstate-AI Worker", version="1.0.0")
# Initialize Evolution Framework components
metrics_collector = MetricsCollector("python_worker")
worker_config = EvolutionConfig(
    database_url=os.getenv("DATABASE_URL", os.getenv("PYTHON_WORKER_DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres"))
)
evolution_manager = FlowstateEvolutionManager(config=worker_config)
anomaly_detector = AnomalyDetector(metrics_collector)
evolution_governor = EvolutionGovernor(evolution_manager, anomaly_detector, metrics_collector)
human_oversight_manager = HumanOversightManager(evolution_manager, evolution_governor, worker_config)
multi_agent_coordinator = MultiAgentCoordinator(
    evolution_manager,
    evolution_governor,
    worker_config,
    human_oversight_manager,
)
performance_tuner = PerformanceTuner(evolution_manager, worker_config)
cost_optimizer = CostOptimizer(evolution_manager, worker_config)
self_modification_orchestrator = SelfModificationOrchestrator(project_root="/home/ubuntu/Flowstate-AI", config_path=None)


class AgentActionRegistry:
    """Tracks pending agent actions that require approvals before execution."""

    def __init__(self):
        self._pending: Dict[str, Dict[str, Any]] = {}
        self.logger = logging.getLogger("agent_action_registry")

    def register_action(
        self,
        event_id: Optional[str],
        *,
        component: str,
        agent_id: str,
        description: str,
        apply_callback: Callable[[], Awaitable[bool]],
    ) -> str:
        """Registers a pending action that can be executed once approved."""
        action_id = event_id or str(uuid.uuid4())
        self._pending[action_id] = {
            "component": component,
            "agent_id": agent_id,
            "description": description,
            "apply_callback": apply_callback,
            "created_at": datetime.utcnow().isoformat(),
        }
        self.logger.info(
            "Registered pending agent action",
            extra={"event_id": action_id, "agent_id": agent_id, "component": component},
        )
        return action_id

    async def execute_action(self, event_id: str) -> Dict[str, Any]:
        """Executes the pending action if it exists."""
        action = self._pending.get(event_id)
        if not action:
            return {"event_id": event_id, "executed": False, "reason": "not_found"}

        callback = action["apply_callback"]
        try:
            success = await callback()
            if success:
                self._pending.pop(event_id, None)
            else:
                action["last_error"] = "apply_callback_returned_false"
            return {"event_id": event_id, "executed": success, "component": action["component"]}
        except Exception as exc:  # pragma: no cover - defensive logging
            self.logger.error(f"Error executing action {event_id}: {exc}")
            action["last_error"] = str(exc)
            return {"event_id": event_id, "executed": False, "reason": str(exc)}

    def list_pending_actions(self) -> List[Dict[str, Any]]:
        return [
            {
                "event_id": event_id,
                "component": payload["component"],
                "agent_id": payload["agent_id"],
                "description": payload["description"],
                "created_at": payload["created_at"],
                "last_error": payload.get("last_error"),
            }
            for event_id, payload in self._pending.items()
        ]


action_registry = AgentActionRegistry()


class PerformanceTuningAgent:
    def __init__(self, tuner: PerformanceTuner, registry: AgentActionRegistry):
        self.tuner = tuner
        self.registry = registry
        self.agent_id = "performance_tuner"

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        component = context.get("component", "core_system")
        metrics = context.get("metrics", {})
        result = await self.tuner.analyze_and_tune(component, metrics)
        if result.get("status") == "proposed":
            event_id = result.get("event_id")

            async def _apply() -> bool:
                return await self.tuner.apply_caching_optimization(component, event_id)

            registered_id = self.registry.register_action(
                event_id,
                component=component,
                agent_id=self.agent_id,
                description=f"Apply caching optimization for {component}",
                apply_callback=_apply,
            )
            result["event_id"] = registered_id
        return result


class CostOptimizationAgent:
    def __init__(self, optimizer: CostOptimizer, registry: AgentActionRegistry):
        self.optimizer = optimizer
        self.registry = registry
        self.agent_id = "cost_optimizer"

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        component = context.get("component", "core_system")
        metrics = context.get("cost_metrics", context.get("metrics", {}))
        result = await self.optimizer.analyze_and_optimize(component, metrics)
        if result.get("status") == "proposed":
            event_id = result.get("event_id")

            async def _apply() -> bool:
                return await self.optimizer.apply_resource_optimization(component, event_id)

            registered_id = self.registry.register_action(
                event_id,
                component=component,
                agent_id=self.agent_id,
                description=f"Apply resource optimization for {component}",
                apply_callback=_apply,
            )
            result["event_id"] = registered_id
        return result


performance_agent = PerformanceTuningAgent(performance_tuner, action_registry)
cost_agent = CostOptimizationAgent(cost_optimizer, action_registry)

multi_agent_coordinator.register_agent(
    "performance_tuner_agent",
    performance_agent,
    ["kpi_analysis", "performance_tuning", "anomaly_response"],
)
multi_agent_coordinator.register_agent(
    "cost_optimizer_agent",
    cost_agent,
    ["crm_signal_processing", "cost_optimization", "resource_management"],
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Setup logging
logger = setup_logging(__name__, "python-worker.log")


class EvolutionSignal(BaseModel):
    source: Literal["kpi", "crm", "system"] = "kpi"
    signal_type: str
    component: str
    metrics: Optional[Dict[str, Any]] = None
    cost_metrics: Optional[Dict[str, Any]] = None
    risk_level: Literal["low", "medium", "high"] = "medium"
    notes: Optional[str] = None


class ApprovalDecision(BaseModel):
    decision: Literal["approve", "reject"]
    rationale: str
    decision_maker: str

class ReminderRequest(BaseModel):
    customer_id: str
    type: str
    message: str
    scheduled_for: datetime

class NBARequest(BaseModel):
    customer_id: Optional[str] = None
    limit: int = 10

@app.get("/")
async def root():
    return {
        "message": "Flowstate-AI Python Worker",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/reminders")
async def create_reminder(reminder: ReminderRequest):
    """Create a new reminder"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders", json={
                "customer_id": reminder.customer_id,
                "type": reminder.type,
                "message": reminder.message,
                "scheduled_for": reminder.scheduled_for.isoformat()
            })
            response.raise_for_status()
            result = response.json()
        return result
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reminders/due")
async def get_due_reminders():
    """Get all reminders that are due"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_API_URL}/reminders/due")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str):
    """Mark a reminder as complete"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/{reminder_id}/complete")
            response.raise_for_status()
            result = response.json()
            if not result:
                raise HTTPException(status_code=404, detail="Reminder not found")
            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing reminder {reminder_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/process-due")
async def process_due_reminders():
    """Process all due reminders and create follow-up actions"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/process-due")
            response.raise_for_status()
            results = response.json()
        return {"processed": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error processing due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba")
async def get_next_best_actions(customer_id: Optional[str] = None, limit: int = 10):
    """Get Next Best Actions (NBA) recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"limit": limit}
            if customer_id:
                params["customer_id"] = customer_id
            response = await client.get(f"{BACKEND_API_URL}/nba", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching NBA recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nba/analyze")
async def analyze_customer_data():
    """Analyze customer data and generate NBA recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/nba/analyze")
            response.raise_for_status()
            results = response.json()
        return {"analyzed": len(results), "recommendations": results}
    except Exception as e:
        logger.error(f"Error analyzing customer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-experimentation")
async def run_autonomous_experimentation():
    """Trigger a cycle of autonomous experimentation and self-modification."""
    try:
        logger.info("Initiating autonomous experimentation cycle...")
        self_modification_orchestrator.run_self_modification_cycle()
        logger.info("Autonomous experimentation cycle completed.")
        return {"status": "success", "message": "Autonomous experimentation cycle initiated."}
    except Exception as e:
        logger.error(f"Error during autonomous experimentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evolution/agents")
async def list_registered_agents():
    """Expose agent registry metadata to dashboards."""
    return {"agents": multi_agent_coordinator.get_agent_status()}


@app.get("/evolution/approvals")
async def get_pending_approvals():
    """Return pending human approvals and queued agent actions."""
    pending = human_oversight_manager.get_pending_approvals()
    return {
        "pending": pending,
        "pending_actions": action_registry.list_pending_actions(),
    }


@app.post("/evolution/approvals/{event_id}")
async def record_approval_decision(event_id: str, decision: ApprovalDecision):
    """Record a human approval/rejection and execute pending actions when approved."""
    recorded = human_oversight_manager.record_human_decision(
        event_id,
        decision=decision.decision,
        rationale=decision.rationale,
        decision_maker=decision.decision_maker,
    )
    apply_result: Optional[Dict[str, Any]] = None
    if recorded and decision.decision == "approve":
        apply_result = await action_registry.execute_action(event_id)
    return {"recorded": recorded, "apply_result": apply_result}


@app.post("/evolution/signals")
async def process_evolution_signal(signal: EvolutionSignal):
    """Route KPI/CRM signals to the appropriate agent via the multi-agent coordinator."""
    capabilities = ["performance_tuning"] if signal.source == "kpi" else ["cost_optimization"]
    task_description = f"{signal.signal_type}:{signal.component}"
    context = {
        "component": signal.component,
        "metrics": signal.metrics,
        "cost_metrics": signal.cost_metrics,
        "risk_level": signal.risk_level,
        "notes": signal.notes,
        "requires_human_oversight": signal.risk_level == "high",
        "signal_type": signal.signal_type,
        "source": signal.source,
    }

    coordination_result = await multi_agent_coordinator.coordinate_task(
        task_description,
        required_capabilities=capabilities,
        context=context,
    )
    return coordination_result

if __name__ == "__main__":
    port = int(os.getenv("PYTHON_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
