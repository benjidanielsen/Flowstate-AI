import logging
from typing import List, Dict, Any

from .evolution_manager import EvolutionManager
from .evolution_governor import EvolutionGovernor
from .config import EvolutionConfig

class MultiAgentCoordinator:
    """Coordinates multiple AI agents for complex tasks and autonomous operations."""

    def __init__(self, evolution_manager: EvolutionManager, governor: EvolutionGovernor, config: EvolutionConfig):
        self.evolution_manager = evolution_manager
        self.governor = governor
        self.config = config
        self.logger = logging.getLogger("multi_agent_coordinator")
        self.active_agents: Dict[str, Any] = {}

        self.logger.info("Multi-Agent Coordinator initialized.")

    def register_agent(self, agent_id: str, agent_instance: Any, capabilities: List[str]):
        """Registers an AI agent with its capabilities."""
        if agent_id in self.active_agents:
            self.logger.warning(f"Agent {agent_id} already registered. Updating capabilities.")
        self.active_agents[agent_id] = {
            "instance": agent_instance,
            "capabilities": capabilities,
            "status": "active",
            "last_heartbeat": self.evolution_manager.metrics_collector.get_current_timestamp()
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

