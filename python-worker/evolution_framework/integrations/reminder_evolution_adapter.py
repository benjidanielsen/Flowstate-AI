"""
Reminder Evolution Adapter

Integrates the Evolution Framework with the Reminder system.
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from ..evolution_manager import EvolutionManager
from ..knowledge_manager import VectorKnowledgeManager
from ..metrics_collector import MetricsCollector


class ReminderEvolutionAdapter:
    """Adapter for integrating evolution capabilities with the Reminder system."""
    
    def __init__(
        self,
        evolution_manager: EvolutionManager,
        knowledge_manager: VectorKnowledgeManager,
        metrics_collector: MetricsCollector
    ):
        """
        Initialize the Reminder evolution adapter.
        
        Args:
            evolution_manager: Evolution manager instance
            knowledge_manager: Knowledge manager instance
            metrics_collector: Metrics collector instance
        """
        self.evolution_manager = evolution_manager
        self.knowledge_manager = knowledge_manager
        self.metrics_collector = metrics_collector
        self.logger = logging.getLogger("reminder_evolution_adapter")
    
    def record_reminder_creation(
        self,
        reminder_id: str,
        reminder_data: Dict[str, Any]
    ) -> None:
        """
        Record a reminder creation for learning and evolution.
        
        Args:
            reminder_id: Reminder identifier
            reminder_data: Reminder details
        """
        try:
            # Record metrics
            self.metrics_collector.record_metric(
                "reminder_created",
                1,
                "count",
                "reminder_system"
            )
            
            # Store in knowledge base
            self.knowledge_manager.add_knowledge(
                content=f"Reminder created: {reminder_data.get('type', 'unknown')}",
                category="pattern",
                source="reminder_system",
                confidence=0.8,
                metadata={
                    "reminder_id": reminder_id,
                    "type": reminder_data.get('type'),
                    "customer_id": reminder_data.get('customer_id'),
                    "scheduled_for": reminder_data.get('scheduled_for'),
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Recorded reminder creation: {reminder_id}")
        
        except Exception as e:
            self.logger.error(f"Error recording reminder creation: {e}")
    
    def record_reminder_execution(
        self,
        reminder_id: str,
        execution_result: Dict[str, Any]
    ) -> None:
        """
        Record reminder execution outcome for learning.
        
        Args:
            reminder_id: Reminder identifier
            execution_result: Execution result details
        """
        try:
            # Record metrics
            if execution_result.get('success'):
                self.metrics_collector.record_metric(
                    "reminder_execution_success",
                    1,
                    "count",
                    "reminder_system"
                )
            else:
                self.metrics_collector.record_metric(
                    "reminder_execution_failure",
                    1,
                    "count",
                    "reminder_system"
                )
            
            # Record execution time if available
            if execution_result.get('execution_time'):
                self.metrics_collector.record_metric(
                    "reminder_execution_time",
                    execution_result['execution_time'],
                    "seconds",
                    "reminder_system"
                )
            
            # Store outcome in knowledge base
            category = "outcome" if execution_result.get('success') else "failure"
            
            self.knowledge_manager.add_knowledge(
                content=f"Reminder execution: {'success' if execution_result.get('success') else 'failure'}",
                category=category,
                source="reminder_system",
                confidence=1.0,
                metadata={
                    "reminder_id": reminder_id,
                    "result": execution_result,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Recorded reminder execution: {reminder_id}")
        
        except Exception as e:
            self.logger.error(f"Error recording reminder execution: {e}")
    
    def record_reminder_response(
        self,
        reminder_id: str,
        customer_response: Dict[str, Any]
    ) -> None:
        """
        Record customer response to a reminder for learning.
        
        Args:
            reminder_id: Reminder identifier
            customer_response: Customer response details
        """
        try:
            # Record response metrics
            response_type = customer_response.get('type', 'unknown')
            
            self.metrics_collector.record_metric(
                f"reminder_response_{response_type}",
                1,
                "count",
                "reminder_system"
            )
            
            # Store in knowledge base
            self.knowledge_manager.add_knowledge(
                content=f"Customer response to reminder: {response_type}",
                category="outcome",
                source="reminder_system",
                confidence=0.9,
                metadata={
                    "reminder_id": reminder_id,
                    "response": customer_response,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.logger.debug(f"Recorded customer response for reminder: {reminder_id}")
        
        except Exception as e:
            self.logger.error(f"Error recording reminder response: {e}")
    
    def get_reminder_improvement_suggestions(self) -> List[Dict[str, Any]]:
        """
        Get improvement suggestions for the reminder system based on learned patterns.
        
        Returns:
            List of improvement suggestions
        """
        try:
            # Analyze reminder performance
            analysis = self.analyze_reminder_performance()
            
            suggestions = []
            
            # Check success rate
            if analysis.get('success_rate', 1.0) < 0.8:
                suggestions.append({
                    "type": "performance",
                    "severity": "high",
                    "message": f"Reminder execution success rate is {analysis['success_rate']:.1%}, below target of 80%",
                    "recommendation": "Review reminder execution logic and error handling"
                })
            
            # Check execution time
            avg_execution_time = analysis.get('average_execution_time', 0)
            if avg_execution_time > 5.0:
                suggestions.append({
                    "type": "performance",
                    "severity": "medium",
                    "message": f"Average reminder execution time is {avg_execution_time:.2f}s, above target of 5s",
                    "recommendation": "Optimize reminder execution process"
                })
            
            # Search for failure patterns
            failure_knowledge = self.knowledge_manager.search_knowledge(
                query="reminder execution failure",
                category="failure",
                source="reminder_system",
                limit=10
            )
            
            if len(failure_knowledge) > 5:
                suggestions.append({
                    "type": "pattern",
                    "severity": "high",
                    "message": f"Detected {len(failure_knowledge)} recent reminder failures",
                    "recommendation": "Analyze failure patterns and implement preventive measures"
                })
            
            return suggestions
        
        except Exception as e:
            self.logger.error(f"Error getting reminder improvement suggestions: {e}")
            return []
    
    def propose_reminder_timing_optimization(
        self,
        customer_segment: str,
        current_timing: Dict[str, Any],
        response_data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Propose optimization for reminder timing based on customer response patterns.
        
        Args:
            customer_segment: Customer segment identifier
            current_timing: Current timing configuration
            response_data: Historical response data
            
        Returns:
            Proposed timing optimization, or None if no improvement suggested
        """
        try:
            # Create evolution event
            event_id = self.evolution_manager.propose_improvement(
                component=f"reminder_timing_{customer_segment}",
                description=f"Reminder timing optimization for {customer_segment}",
                metrics_before=response_data,
                metadata={
                    "customer_segment": customer_segment,
                    "current_timing": current_timing
                }
            )
            
            if not event_id:
                return None
            
            # Search knowledge base for successful timing patterns
            knowledge_results = self.knowledge_manager.search_knowledge(
                query=f"successful reminder timing for {customer_segment}",
                category="outcome",
                limit=5
            )
            
            # Analyze response patterns (placeholder for actual analysis)
            # In production, this would analyze response rates by time of day, day of week, etc.
            
            proposal = {
                "event_id": event_id,
                "customer_segment": customer_segment,
                "current_timing": current_timing,
                "proposed_timing": {
                    "preferred_hours": [9, 10, 14, 15],  # Example optimization
                    "avoid_hours": [0, 1, 2, 3, 4, 5, 6, 7, 22, 23],
                    "preferred_days": ["Tuesday", "Wednesday", "Thursday"]
                },
                "reasoning": "Based on historical response patterns",
                "related_knowledge": knowledge_results,
                "confidence": 0.7
            }
            
            self.logger.info(f"Proposed timing optimization for segment {customer_segment}")
            return proposal
        
        except Exception as e:
            self.logger.error(f"Error proposing reminder timing optimization: {e}")
            return None
    
    def apply_reminder_improvement(
        self,
        proposal: Dict[str, Any]
    ) -> bool:
        """
        Apply an approved reminder system improvement.
        
        Args:
            proposal: Improvement proposal
            
        Returns:
            True if successful, False otherwise
        """
        try:
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
                content=f"Applied reminder system improvement for {proposal.get('customer_segment', 'system')}",
                category="best_practice",
                source="reminder_evolution_adapter",
                confidence=proposal.get('confidence', 0.5),
                metadata={
                    "proposal": proposal,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            self.metrics_collector.record_metric(
                "reminder_improvement_applied",
                1,
                "count",
                "reminder_evolution_adapter"
            )
            
            self.logger.info(f"Applied reminder improvement")
            return True
        
        except Exception as e:
            self.logger.error(f"Error applying reminder improvement: {e}")
            return False
    
    def analyze_reminder_performance(self) -> Dict[str, Any]:
        """
        Analyze overall reminder system performance.
        
        Returns:
            Performance analysis summary
        """
        try:
            # Get metrics
            created = self.metrics_collector.get_metric_stats(
                "reminder_created",
                "reminder_system"
            )
            
            successes = self.metrics_collector.get_metric_stats(
                "reminder_execution_success",
                "reminder_system"
            )
            
            failures = self.metrics_collector.get_metric_stats(
                "reminder_execution_failure",
                "reminder_system"
            )
            
            execution_time = self.metrics_collector.get_metric_stats(
                "reminder_execution_time",
                "reminder_system"
            )
            
            # Calculate metrics
            total_created = created.get('count', 0) if created else 0
            success_count = successes.get('count', 0) if successes else 0
            failure_count = failures.get('count', 0) if failures else 0
            total_executed = success_count + failure_count
            
            success_rate = success_count / total_executed if total_executed > 0 else 0
            
            analysis = {
                "total_created": total_created,
                "total_executed": total_executed,
                "success_count": success_count,
                "failure_count": failure_count,
                "success_rate": success_rate,
                "average_execution_time": execution_time.get('average', 0) if execution_time else 0,
                "timestamp": datetime.now().isoformat()
            }
            
            return analysis
        
        except Exception as e:
            self.logger.error(f"Error analyzing reminder performance: {e}")
            return {}
    
    def optimize_reminder_frequency(
        self,
        customer_id: str,
        current_frequency: int,
        engagement_data: Dict[str, Any]
    ) -> Optional[int]:
        """
        Optimize reminder frequency for a customer based on engagement patterns.
        
        Args:
            customer_id: Customer identifier
            current_frequency: Current reminder frequency (days)
            engagement_data: Historical engagement data
            
        Returns:
            Optimized frequency in days, or None if no change recommended
        """
        try:
            # Analyze engagement patterns
            response_rate = engagement_data.get('response_rate', 0)
            
            # Adjust frequency based on engagement
            if response_rate > 0.8:
                # High engagement - can increase frequency
                new_frequency = max(1, current_frequency - 1)
            elif response_rate < 0.3:
                # Low engagement - decrease frequency
                new_frequency = min(30, current_frequency + 2)
            else:
                # Moderate engagement - maintain current frequency
                new_frequency = current_frequency
            
            if new_frequency != current_frequency:
                # Record the optimization
                self.knowledge_manager.add_knowledge(
                    content=f"Optimized reminder frequency for customer {customer_id}",
                    category="best_practice",
                    source="reminder_evolution_adapter",
                    confidence=0.8,
                    metadata={
                        "customer_id": customer_id,
                        "old_frequency": current_frequency,
                        "new_frequency": new_frequency,
                        "response_rate": response_rate,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                
                return new_frequency
            
            return None
        
        except Exception as e:
            self.logger.error(f"Error optimizing reminder frequency: {e}")
            return None

