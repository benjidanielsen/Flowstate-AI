"""
Evolution Governor

Enforces policies and manages safe mode for the evolution framework.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from .evolution_manager import EvolutionManager
from .anomaly_detector import AnomalyDetector
from .metrics_collector import MetricsCollector
from .knowledge_manager import VectorKnowledgeManager
from .config import EvolutionConfig


class EvolutionGovernor:
    """Enforces evolution policies and manages system safety."""
    
    def __init__(
        self,
        evolution_manager: EvolutionManager,
        anomaly_detector: AnomalyDetector,
        metrics_collector: MetricsCollector,
        knowledge_manager: VectorKnowledgeManager,
        config: Optional[EvolutionConfig] = None
    ):
        """
        Initialize the evolution governor.
        
        Args:
            evolution_manager: Evolution manager instance
            anomaly_detector: Anomaly detector instance
            metrics_collector: Metrics collector instance
            knowledge_manager: Knowledge manager instance
            config: Evolution framework configuration
        """
        self.evolution_manager = evolution_manager
        self.anomaly_detector = anomaly_detector
        self.metrics_collector = metrics_collector
        self.knowledge_manager = knowledge_manager
        self.config = config or EvolutionConfig()
        self.logger = logging.getLogger("evolution_governor")
        
        # Track safe mode state
        self.safe_mode_active = False
        self.safe_mode_reason = None
        self.safe_mode_activated_at = None
        
        # Track policy violations
        self.policy_violations = []
    
    def evaluate_evolution_impact(
        self,
        event_id: str,
        component: str
    ) -> Dict[str, Any]:
        """
        Evaluate the potential impact of a proposed evolution.
        
        Args:
            event_id: Evolution event ID
            component: Component being modified
            
        Returns:
            Impact evaluation results
        """
        self.logger.info(f"Evaluating impact of evolution event: {event_id}")
        
        evaluation = {
            "event_id": event_id,
            "component": component,
            "safe_mode_active": self.safe_mode_active,
            "approved": False,
            "concerns": [],
            "recommendations": []
        }
        
        # Check if safe mode is active
        if self.safe_mode_active:
            evaluation["concerns"].append({
                "type": "safe_mode",
                "severity": "critical",
                "message": f"Safe mode is active: {self.safe_mode_reason}"
            })
            return evaluation
        
        # Check if component requires human oversight
        if component in self.config.human_oversight_required:
            evaluation["concerns"].append({
                "type": "human_oversight",
                "severity": "high",
                "message": f"Component '{component}' requires human oversight"
            })
            evaluation["recommendations"].append("Request human approval before proceeding")
        
        # Check for recent anomalies
        recent_anomalies = self.anomaly_detector.get_anomaly_report(hours=1)
        if recent_anomalies['total_anomalies'] > 0:
            evaluation["concerns"].append({
                "type": "recent_anomalies",
                "severity": "high",
                "message": f"Detected {recent_anomalies['total_anomalies']} anomalies in the last hour"
            })
            evaluation["recommendations"].append("Investigate anomalies before proceeding")
        
        # Check cost constraints
        # (In production, this would check actual cost metrics)
        
        # Approve if no critical concerns
        critical_concerns = [
            c for c in evaluation["concerns"]
            if c["severity"] == "critical"
        ]
        
        if not critical_concerns:
            evaluation["approved"] = True
        
        return evaluation
    
    def activate_safe_mode(self, reason: str = "unknown") -> None:
        """
        Activate safe mode to halt automatic evolution.
        
        Args:
            reason: Reason for activating safe mode
        """
        if self.safe_mode_active:
            self.logger.warning(f"Safe mode already active: {self.safe_mode_reason}")
            return
        
        self.safe_mode_active = True
        self.safe_mode_reason = reason
        self.safe_mode_activated_at = datetime.now()
        
        self.logger.critical(
            f"SAFE MODE ACTIVATED - Automatic evolution halted. Reason: {reason}"
        )
        
        # Record in knowledge base
        self.knowledge_manager.add_knowledge(
            content=f"Safe mode activated: {reason}",
            category="failure",
            source="evolution_governor",
            confidence=1.0,
            metadata={
                "action": "safe_mode_activate",
                "reason": reason,
                "timestamp": self.safe_mode_activated_at.isoformat()
            }
        )
        
        # Record metric
        self.metrics_collector.record_metric(
            "safe_mode_activation",
            1,
            "count",
            "evolution_governor"
        )
    
    def deactivate_safe_mode(self, reason: str = "manual_override") -> None:
        """
        Deactivate safe mode to resume automatic evolution.
        
        Args:
            reason: Reason for deactivating safe mode
        """
        if not self.safe_mode_active:
            self.logger.warning("Safe mode is not active")
            return
        
        previous_reason = self.safe_mode_reason
        self.safe_mode_active = False
        self.safe_mode_reason = None
        self.safe_mode_activated_at = None
        
        self.logger.info(
            f"Safe mode deactivated. Automatic evolution resumed. Reason: {reason}"
        )
        
        # Record in knowledge base
        self.knowledge_manager.add_knowledge(
            content=f"Safe mode deactivated: {reason}",
            category="outcome",
            source="evolution_governor",
            confidence=1.0,
            metadata={
                "action": "safe_mode_deactivate",
                "reason": reason,
                "previous_reason": previous_reason,
                "timestamp": datetime.now().isoformat()
            }
        )
        
        # Record metric
        self.metrics_collector.record_metric(
            "safe_mode_deactivation",
            1,
            "count",
            "evolution_governor"
        )
    
    def enforce_policies(self) -> Dict[str, Any]:
        """
        Continuously monitor system and enforce evolution policies.
        
        Returns:
            Policy enforcement summary
        """
        self.logger.info("Enforcing evolution policies")
        
        enforcement_summary = {
            "timestamp": datetime.now().isoformat(),
            "safe_mode_active": self.safe_mode_active,
            "violations": [],
            "actions_taken": []
        }
        
        # Check for anomalies
        anomalies = self.anomaly_detector.monitor_all_metrics()
        
        if anomalies and not self.safe_mode_active:
            critical_anomalies = [
                a for a in anomalies
                if a.get('severity') == 'critical'
            ]
            
            if critical_anomalies:
                self.activate_safe_mode(
                    reason=f"Critical anomalies detected: {len(critical_anomalies)}"
                )
                enforcement_summary["actions_taken"].append({
                    "action": "safe_mode_activated",
                    "reason": "critical_anomalies",
                    "count": len(critical_anomalies)
                })
        
        # Check cost constraints
        # (In production, this would check actual cost metrics)
        
        # Check modification rate limits
        recent_modifications = self.metrics_collector.get_metric_stats(
            "modification_applied",
            "self_modification_orchestrator",
            limit=100
        )
        
        if recent_modifications and recent_modifications['count'] > 50:
            # Too many modifications in a short time
            if not self.safe_mode_active:
                self.activate_safe_mode(
                    reason="Excessive modification rate detected"
                )
                enforcement_summary["actions_taken"].append({
                    "action": "safe_mode_activated",
                    "reason": "excessive_modifications",
                    "count": recent_modifications['count']
                })
        
        # Check for repeated failures
        # (In production, this would analyze failure patterns)
        
        return enforcement_summary
    
    def check_component_authorization(self, component: str) -> Dict[str, Any]:
        """
        Check if a component is authorized for modification.
        
        Args:
            component: Component name
            
        Returns:
            Authorization check results
        """
        authorization = {
            "component": component,
            "authorized": False,
            "requires_human_oversight": False,
            "reason": None
        }
        
        # Check if component is in allowed list
        if component in self.config.allowed_modifications:
            authorization["authorized"] = True
            authorization["reason"] = "Component in allowed modifications list"
        
        # Check if component requires human oversight
        if component in self.config.human_oversight_required:
            authorization["requires_human_oversight"] = True
            authorization["reason"] = "Component requires human oversight"
        
        # If not explicitly allowed, deny
        if not authorization["authorized"]:
            authorization["reason"] = "Component not in allowed modifications list"
        
        return authorization
    
    def record_policy_violation(
        self,
        violation_type: str,
        component: str,
        details: Dict[str, Any]
    ) -> None:
        """
        Record a policy violation.
        
        Args:
            violation_type: Type of violation
            component: Component involved
            details: Violation details
        """
        violation = {
            "timestamp": datetime.now().isoformat(),
            "type": violation_type,
            "component": component,
            "details": details
        }
        
        self.policy_violations.append(violation)
        
        self.logger.warning(
            f"Policy violation recorded: {violation_type} on {component}"
        )
        
        # Record in knowledge base
        self.knowledge_manager.add_knowledge(
            content=f"Policy violation: {violation_type}",
            category="failure",
            source="evolution_governor",
            confidence=1.0,
            metadata=violation
        )
        
        # Record metric
        self.metrics_collector.record_metric(
            "policy_violation",
            1,
            "count",
            "evolution_governor"
        )
    
    def get_governance_status(self) -> Dict[str, Any]:
        """
        Get current governance status.
        
        Returns:
            Governance status dictionary
        """
        return {
            "safe_mode_active": self.safe_mode_active,
            "safe_mode_reason": self.safe_mode_reason,
            "safe_mode_activated_at": (
                self.safe_mode_activated_at.isoformat()
                if self.safe_mode_activated_at else None
            ),
            "recent_violations": len([
                v for v in self.policy_violations
                if (datetime.now() - datetime.fromisoformat(v['timestamp'])).total_seconds() < 3600
            ]),
            "total_violations": len(self.policy_violations),
            "allowed_modifications": self.config.allowed_modifications,
            "human_oversight_required": self.config.human_oversight_required
        }
    
    def reset_violations(self) -> int:
        """
        Clear recorded policy violations.
        
        Returns:
            Number of violations cleared
        """
        count = len(self.policy_violations)
        self.policy_violations = []
        self.logger.info(f"Cleared {count} policy violations")
        return count

