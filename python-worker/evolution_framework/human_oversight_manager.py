import logging
from typing import Any, Dict, List, Optional

from .evolution_manager import EvolutionManager
from .evolution_governor import EvolutionGovernor
from .config import EvolutionConfig

class HumanOversightManager:
    """Manages human oversight and intervention points within the autonomous system."""

    def __init__(self, evolution_manager: EvolutionManager, governor: EvolutionGovernor, config: EvolutionConfig):
        self.evolution_manager = evolution_manager
        self.governor = governor
        self.config = config
        self.logger = logging.getLogger("human_oversight_manager")
        self.pending_approvals: Dict[str, Any] = {}

        self.logger.info("Human Oversight Manager initialized.")

    def request_human_approval(self, action_description: str, context: Dict[str, Any], urgency: str = "medium") -> str:
        """Requests human approval for a critical action or decision."""
        event_id = self.evolution_manager.create_evolution_event(
            event_type="human_approval_request",
            component="system",
            description=f"Requesting human approval for: {action_description}",
            proposed_by="human_oversight_manager",
            status="pending_human_approval",
            metadata={
                "action_description": action_description,
                "context": context,
                "urgency": urgency
            }
        )
        if event_id:
            self.pending_approvals[event_id] = {
                "action_description": action_description,
                "context": context,
                "urgency": urgency,
                "timestamp": self.evolution_manager.metrics_collector.get_current_timestamp()
            }
            self.logger.warning(f"Human approval requested for event {event_id}: {action_description}")
        return event_id

    def record_human_decision(self, event_id: str, decision: str, rationale: str, decision_maker: str) -> bool:
        """Records a human decision for a previously requested approval."""
        if event_id not in self.pending_approvals:
            self.logger.warning(f"No pending approval request found for event {event_id}")
            return False

        status = "approved" if decision.lower() == "approve" else "rejected"
        success = self.evolution_manager.update_evolution_event(
            event_id,
            status=status,
            metadata={
                "human_decision": decision,
                "rationale": rationale,
                "decision_maker": decision_maker,
                "decision_timestamp": self.evolution_manager.metrics_collector.get_current_timestamp()
            }
        )
        if success:
            del self.pending_approvals[event_id]
            self.logger.info(f"Human decision recorded for event {event_id}: {decision} by {decision_maker}")
        return success

    def get_pending_approvals(self) -> List[Dict[str, Any]]:
        """Retrieves all pending human approval requests."""
        pending_events = self.evolution_manager.get_evolution_events(status="pending_human_approval")
        return [{
            "event_id": event["id"],
            "action_description": event["metadata"].get("action_description"),
            "context": event["metadata"].get("context"),
            "urgency": event["metadata"].get("urgency"),
            "timestamp": event["timestamp"]
        } for event in pending_events]

    def check_human_decision(self, event_id: str) -> Optional[str]:
        """Checks the decision made for a specific human approval request."""
        event = self.evolution_manager.get_evolution_events(event_type="human_approval_request", status="approved", limit=1)
        if event and event[0]["id"] == event_id:
            return "approved"
        event = self.evolution_manager.get_evolution_events(event_type="human_approval_request", status="rejected", limit=1)
        if event and event[0]["id"] == event_id:
            return "rejected"
        return None

