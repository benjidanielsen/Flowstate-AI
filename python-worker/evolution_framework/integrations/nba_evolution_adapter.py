"""
NBA Evolution Adapter

Integrates the Evolution Framework with the Next Best Action (NBA) engine.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
from ..evolution_manager import EvolutionManager
from ..knowledge_manager import VectorKnowledgeManager
from ..metrics_collector import MetricsCollector


class NBAEvolutionAdapter:
    """Adapter for integrating evolution capabilities with the NBA engine."""
    
    def __init__(
        self,
        evolution_manager: EvolutionManager,
        knowledge_manager: VectorKnowledgeManager,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the NBA evolution adapter.
        
        Args:
            evolution_manager: Evolution manager instance
            knowledge_manager: Knowledge manager instance
            metrics_collector: Metrics collector instance
        """
        self.evolution_manager = evolution_manager
        self.knowledge_manager = knowledge_manager
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger("nba_evolution_adapter")
    
    def record_nba_decision(
        self,
        customer_id: str,
        decision: Dict[str, Any],
        context: Dict[str, Any]
    ) -> None:
        """
        Record an NBA decision for learning and evolution.
        
        Args:
            customer_id: Customer identifier
            decision: NBA decision details
            context: Decision context
        """
        try:
            # Record metrics
            self.metrics_collector.record_metric(
                "nba_decision_made",
                1,
                "count",
                "nba_engine"
            )
            
            if decision.get('confidence'):
                self.metrics_collector.record_metric(
                    "nba_decision_confidence",
                    decision['confidence'],
                    "score",
                    "nba_engine"
                )
            
            # Store decision in knowledge base for pattern learning
            self.knowledge_manager.add_knowledge(
                content=f"NBA decision for customer {customer_id}: {decision.get('action_type', 'unknown')}",
                category="pattern",
                source="nba_engine",
                confidence=decision.get('confidence', 0.5),
                metadata={
                    "customer_id": customer_id,
                    "action_type": decision.get('action_type'),
                    "decision": decision,
                    "context": context,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Recorded NBA decision for customer {customer_id}")
        
        except Exception as e:
            self.logger.error(f"Error recording NBA decision: {e}")
    
    def record_nba_outcome(
        self,
        customer_id: str,
        decision_id: str,
        outcome: Dict[str, Any]
    ) -> None:
        """
        Record the outcome of an NBA decision for learning.
        
        Args:
            customer_id: Customer identifier
            decision_id: Decision identifier
            outcome: Outcome details (success, failure, metrics)
        """
        try:
            # Record outcome metrics
            if outcome.get('success'):
                self.metrics_collector.record_metric(
                    "nba_decision_success",
                    1,
                    "count",
                    "nba_engine"
                )
            else:
                self.metrics_collector.record_metric(
                    "nba_decision_failure",
                    1,
                    "count",
                    "nba_engine"
                )
            
            # Store outcome in knowledge base
            category = "outcome" if outcome.get('success') else "failure"
            
            self.knowledge_manager.add_knowledge(
                content=f"NBA outcome for decision {decision_id}: {'success' if outcome.get('success') else 'failure'}",
                category=category,
                source="nba_engine",
                confidence=1.0,
                metadata={
                    "customer_id": customer_id,
                    "decision_id": decision_id,
                    "outcome": outcome,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Recorded NBA outcome for decision {decision_id}")
        
        except Exception as e:
            self.logger.error(f"Error recording NBA outcome: {e}")
    
    def get_nba_improvement_suggestions(
        self,
        context: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get improvement suggestions for the NBA engine based on learned patterns.
        
        Args:
            context: Optional context for filtering suggestions
            
        Returns:
            List of improvement suggestions
        """
        try:
            # Search knowledge base for relevant patterns
            query = "NBA decision patterns and outcomes"
            if context:
                query += f" for {context.get('customer_segment', 'all customers')}"
            
            knowledge_results = self.knowledge_manager.search_knowledge(
                query=query,
                category="outcome",
                source="nba_engine",
                limit=10
            )
            
            # Analyze patterns to generate suggestions
            suggestions = []
            
            # Calculate success rate
            success_count = sum(
                1 for k in knowledge_results
                if 'success' in k.get('content', '').lower()
            )
            total_count = len(knowledge_results)
            
            if total_count > 0:
                success_rate = success_count / total_count
                
                if success_rate < 0.7:
                    suggestions.append({
                        "type": "performance",
                        "severity": "medium",
                        "message": f"NBA success rate is {success_rate:.1%}, below target of 70%",
                        "recommendation": "Review decision logic and consider adjusting confidence thresholds"
                    })
            
            # Check for patterns in failures
            failure_patterns = [
                k for k in knowledge_results
                if 'failure' in k.get('content', '').lower()
            ]
            
            if len(failure_patterns) > 3:
                suggestions.append({
                    "type": "pattern",
                    "severity": "high",
                    "message": f"Detected {len(failure_patterns)} failure patterns",
                    "recommendation": "Analyze common failure characteristics and adjust NBA rules"
                })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"Error getting NBA improvement suggestions: {e}")
            return []
    
    def propose_nba_rule_improvement(
        self,
        rule_id: str,
        current_rule: Dict[str, Any],
        performance_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Propose an improvement to an NBA rule based on performance data.
        
        Args:
            rule_id: Rule identifier
            current_rule: Current rule definition
            performance_data: Performance metrics for the rule
            
        Returns:
            Proposed improvement, or None if no improvement suggested
        """
        try:
            # Create evolution event
            event_id = self.evolution_manager.propose_improvement(
                component=f"nba_rule_{rule_id}",
                description=f"NBA rule improvement based on performance analysis",
                metrics_before=performance_data,
                metadata={
                    "rule_id": rule_id,
                    "current_rule": current_rule
                }
            )
            
            if not event_id:
                return None
            
            # Search knowledge base for similar successful patterns
            knowledge_results = self.knowledge_manager.search_knowledge(
                query=f"successful NBA decisions similar to rule {rule_id}",
                category="outcome",
                limit=5
            )
            
            # Generate improvement proposal (placeholder for LLM integration)
            proposal = {
                "event_id": event_id,
                "rule_id": rule_id,
                "current_rule": current_rule,
                "proposed_changes": {
                    "confidence_threshold": current_rule.get('confidence_threshold', 0.7) + 0.05,
                    "priority": current_rule.get('priority', 5) + 1
                },
                "reasoning": "Adjusting based on performance patterns",
                "related_knowledge": knowledge_results,
                "confidence": 0.75
            }
            
            self.logger.info(f"Proposed improvement for NBA rule {rule_id}")
            return proposal
        
        except Exception as e:
            self.logger.error(f"Error proposing NBA rule improvement: {e}")
            return None
    
    def apply_nba_improvement(
        self,
        proposal: Dict[str, Any]
    ) -> bool:
        """
        Apply an approved NBA improvement.
        
        Args:
            proposal: Improvement proposal
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # In production, this would update the NBA rule in the database
            # For now, we'll just mark the evolution event as applied
            
            event_id = proposal.get('event_id')
            if not event_id:
                self.logger.error("No event_id in proposal")
                return False
            
            # Mark as applied
            self.evolution_manager.apply_improvement(
                event_id=event_id,
                metrics_after={"status": "applied"}
            )
            
            # Record in knowledge base
            self.knowledge_manager.add_knowledge(
                content=f"Applied NBA rule improvement for {proposal.get('rule_id')}",
                category="best_practice",
                source="nba_evolution_adapter",
                confidence=proposal.get('confidence', 0.5),
                metadata={
                    "rule_id": proposal.get('rule_id'),
                    "changes": proposal.get('proposed_changes'),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.metrics_collector.record_metric(
                "nba_improvement_applied",
                1,
                "count",
                "nba_evolution_adapter"
            )
            
            self.logger.info(f"Applied NBA improvement for rule {proposal.get('rule_id')}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying NBA improvement: {e}")
            return False
    
    def analyze_nba_performance(self) -> Dict[str, Any]:
        """
        Analyze overall NBA engine performance.
        
        Returns:
            Performance analysis summary
        """
        try:
            # Get metrics
            decisions_made = self.metrics_collector.get_metric_stats(
                "nba_decision_made",
                "nba_engine"
            )
            
            successes = self.metrics_collector.get_metric_stats(
                "nba_decision_success",
                "nba_engine"
            )
            
            failures = self.metrics_collector.get_metric_stats(
                "nba_decision_failure",
                "nba_engine"
            )
            
            avg_confidence = self.metrics_collector.get_metric_stats(
                "nba_decision_confidence",
                "nba_engine"
            )
            
            # Calculate metrics
            total_decisions = decisions_made.get('count', 0) if decisions_made else 0
            success_count = successes.get('count', 0) if successes else 0
            failure_count = failures.get('count', 0) if failures else 0
            
            success_rate = success_count / total_decisions if total_decisions > 0 else 0
            
            analysis = {
                "total_decisions": total_decisions,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": success_rate,
                "average_confidence": avg_confidence.get('average', 0) if avg_confidence else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing NBA performance: {e}")
            return {}

