import logging
from typing import List, Dict, Any, Optional

from .evolution_manager import EvolutionManager
from .evolution_governor import EvolutionGovernor
from .config import EvolutionConfig
from .human_oversight_manager import HumanOversightManager

class MultiAgentCoordinator:
    """Coordinates multiple AI agents for complex tasks and autonomous operations."""

    def __init__(
        self,
        evolution_manager: EvolutionManager,
        governor: EvolutionGovernor,
        config: EvolutionConfig,
        human_oversight_manager: Optional[HumanOversightManager] = None,
    ):
        self.evolution_manager = evolution_manager
        self.governor = governor
        self.config = config
        self.human_oversight_manager = human_oversight_manager
        self.logger = logging.getLogger("multi_agent_coordinator")
        self.active_agents: Dict[str, Any] = {}

        self.logger.info("Multi-Agent Coordinator initialized.")

    def register_agent(self, agent_id: str, agent_instance: Any, capabilities: List[str]):
        """Registers an AI agent with its capabilities."""
        if agent_id in self.active_agents:
            self.logger.warning(f"Agent {agent_id} already registered. Updating capabilities.")
        timestamp = self.evolution_manager.metrics_collector.get_current_timestamp()
        self.active_agents[agent_id] = {
            "instance": agent_instance,
            "capabilities": capabilities,
            "status": "idle",
            "last_heartbeat": timestamp,
            "pending_event_id": None,
            "last_task": None,
        }
        self.logger.info(f"Agent {agent_id} registered with capabilities: {capabilities}")

    def deregister_agent(self, agent_id: str):
        """Deregisters an AI agent."""
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
            self.logger.info(f"Agent {agent_id} deregistered.")
        else:
            self.logger.warning(f"Attempted to deregister non-existent agent {agent_id}")

    async def coordinate_task(self, task_description: str, required_capabilities: List[str], context: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinates a task by assigning it to suitable agents and managing their interaction."""
        self.logger.info(f"Coordinating task: {task_description} with capabilities: {required_capabilities}")

        if not self.governor.check_policy("task_coordination", {"task_description": task_description, "required_capabilities": required_capabilities}):
            self.logger.warning(f"Task coordination for '{task_description}' blocked by governance policy.")
            return {"status": "blocked", "reason": "Governance policy violation"}

        suitable_agents = self._find_suitable_agents(required_capabilities)

        if not suitable_agents:
            self.logger.error(f"No suitable agents found for task: {task_description}")
            return {"status": "failed", "reason": "No suitable agents"}

        # Simplified coordination: assign to first suitable agent
        # In a real scenario, this would involve complex negotiation, task splitting, etc.
        assigned_agent_id = suitable_agents[0]["id"]
        assigned_agent_instance = suitable_agents[0]["instance"]
        self.logger.info(f"Assigning task '{task_description}' to agent {assigned_agent_id}")

        requires_human_approval = self._requires_human_oversight(context)
        if requires_human_approval and self.human_oversight_manager:
            event_id = self.human_oversight_manager.request_human_approval(
                action_description=task_description,
                context=context,
                urgency=context.get("urgency", "high"),
            )
            self.update_agent_status(assigned_agent_id, "waiting_human_approval", pending_event_id=event_id)
            return {
                "status": "pending_human_approval",
                "agent_id": assigned_agent_id,
                "event_id": event_id,
                "reason": "awaiting_human_oversight",
            }

        self.update_agent_status(assigned_agent_id, "executing", task_description=task_description)

        try:
            # Assuming agents have a method to execute tasks
            result = await assigned_agent_instance.execute_task(task_description, context)
            self.evolution_manager.create_evolution_event(
                event_type="agent_task_completed",
                component=assigned_agent_id,
                description=f"Task '{task_description}' completed.",
                proposed_by="multi_agent_coordinator",
                status="completed",
                metadata={
                    "task_description": task_description,
                    "required_capabilities": required_capabilities,
                    "result": result
                }
            )
            self.update_agent_status(assigned_agent_id, "idle")
            return {"status": "success", "agent_id": assigned_agent_id, "result": result}
        except Exception as e:
            self.logger.error(f"Agent {assigned_agent_id} failed to execute task '{task_description}': {e}")
            self.evolution_manager.create_evolution_event(
                event_type="agent_task_failed",
                component=assigned_agent_id,
                description=f"Task '{task_description}' failed.",
                proposed_by="multi_agent_coordinator",
                status="failed",
                metadata={
                    "task_description": task_description,
                    "required_capabilities": required_capabilities,
                    "error": str(e)
                }
            )
            self.update_agent_status(assigned_agent_id, "error")
            return {"status": "failed", "agent_id": assigned_agent_id, "error": str(e)}

    def _find_suitable_agents(self, required_capabilities: List[str]) -> List[Dict[str, Any]]:
        """Finds agents that possess all required capabilities."""
        suitable = []
        for agent_id, agent_data in self.active_agents.items():
            if all(cap in agent_data["capabilities"] for cap in required_capabilities):
                suitable.append({"id": agent_id, "instance": agent_data["instance"]})
        return suitable

    def get_agent_status(self) -> Dict[str, Any]:
        """Returns the status of all registered agents."""
        status = {}
        for agent_id, agent_data in self.active_agents.items():
            status[agent_id] = {
                "capabilities": agent_data["capabilities"],
                "status": agent_data["status"],
                "last_heartbeat": agent_data["last_heartbeat"]
            }
        return status

    def update_agent_status(
        self,
        agent_id: str,
        status: str,
        *,
        pending_event_id: Optional[str] = None,
        task_description: Optional[str] = None,
    ) -> None:
        """Updates runtime status metadata for an agent."""
        agent = self.active_agents.get(agent_id)
        if not agent:
            self.logger.warning(f"Attempted to update status for unknown agent {agent_id}")
            return

        agent["status"] = status
        agent["last_heartbeat"] = self.evolution_manager.metrics_collector.get_current_timestamp()
        if pending_event_id is not None:
            agent["pending_event_id"] = pending_event_id
        if task_description is not None:
            agent["last_task"] = task_description

    def record_heartbeat(self, agent_id: str) -> None:
        """Updates the heartbeat timestamp for an active agent."""
        agent = self.active_agents.get(agent_id)
        if agent:
            agent["last_heartbeat"] = self.evolution_manager.metrics_collector.get_current_timestamp()

    def _requires_human_oversight(self, context: Optional[Dict[str, Any]]) -> bool:
        """Determines whether the provided context needs human oversight."""
        if not context:
            return False

        if context.get("risk_level", "low").lower() == "high":
            return True

        if context.get("requires_human_oversight"):
            return True

        component = context.get("component")
        if component and component in self.config.human_oversight_required:
            return True

        return False

