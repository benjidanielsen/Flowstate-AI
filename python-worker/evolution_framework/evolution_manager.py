"""
Evolution Manager

Core orchestrator for the Evolution Framework, coordinating self-improvement activities.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import Json
import requests
from .config import EvolutionConfig
from .metrics_collector import MetricsCollector


class EvolutionManager:
    """Manages the evolution process for Flowstate-AI."""
    
    def __init__(self, config: Optional[EvolutionConfig] = None):
        """
        Initialize the evolution manager.
        
        Args:
            config: Evolution framework configuration
        """
        self.config = config or EvolutionConfig()
        self.config.validate()
        self.logger = logging.getLogger("evolution_manager")
        self.metrics_collector = MetricsCollector("evolution_manager", self.config)
        self._conn = None
        
        self.logger.info("Evolution Manager initialized")
        if self.config.safe_mode:
            self.logger.warning("Evolution Manager started in SAFE MODE")
    
    def _get_connection(self):
        """Get database connection."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.config.database_url)
        return self._conn
    
    def is_enabled(self) -> bool:
        """Check if evolution is enabled."""
        return self.config.enabled and not self.config.safe_mode
    
    def create_evolution_event(
        self,
        event_type: str,
        component: str,
        description: str,
        proposed_by: str,
        status: str = "proposed",
        metrics_before: Optional[Dict[str, Any]] = None,
        metrics_after: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Create an evolution event record.
        
        Args:
            event_type: Type of evolution event
            component: Component being modified
            description: Description of the change
            proposed_by: Who/what proposed the change
            status: Current status
            metrics_before: Metrics before change
            metrics_after: Metrics after change
            metadata: Additional metadata
            
        Returns:
            Event ID if successful, None otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            event_id = str(uuid.uuid4())
            
            cursor.execute(
                """
                INSERT INTO evolution_events 
                (id, type, component, description, proposed_by, status, 
                 metrics_before, metrics_after, metadata)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
                """,
                (
                    event_id,
                    event_type,
                    component,
                    description,
                    proposed_by,
                    status,
                    Json(metrics_before or {}),
                    Json(metrics_after or {}),
                    Json(metadata or {})
                )
            )
            
            conn.commit()
            cursor.close()
            
            self.logger.info(
                f"Created evolution event: {event_id} - {event_type} for {component}"
            )
            return event_id
            
        except Exception as e:
            self.logger.error(f"Error creating evolution event: {e}")
            return None
    
    def update_evolution_event(
        self,
        event_id: str,
        status: Optional[str] = None,
        metrics_after: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing evolution event.
        
        Args:
            event_id: ID of the event to update
            status: New status
            metrics_after: Metrics after change
            metadata: Additional metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            updates = []
            params = []
            
            if status:
                updates.append("status = %s")
                params.append(status)
            
            if metrics_after:
                updates.append("metrics_after = %s")
                params.append(Json(metrics_after))
            
            if metadata:
                updates.append("metadata = %s")
                params.append(Json(metadata))
            
            if not updates:
                return True
            
            updates.append("updated_at = NOW()")
            params.append(event_id)
            
            query = f"""
                UPDATE evolution_events 
                SET {', '.join(updates)}
                WHERE id = %s
            """
            
            cursor.execute(query, params)
            conn.commit()
            cursor.close()
            
            self.logger.info(f"Updated evolution event: {event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating evolution event: {e}")
            return False
    
    def get_evolution_events(
        self,
        event_type: Optional[str] = None,
        component: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Retrieve evolution events.
        
        Args:
            event_type: Filter by event type
            component: Filter by component
            status: Filter by status
            limit: Maximum number of results
            
        Returns:
            List of evolution events
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = "SELECT * FROM evolution_events WHERE 1=1"
            params = []
            
            if event_type:
                query += " AND type = %s"
                params.append(event_type)
            
            if component:
                query += " AND component = %s"
                params.append(component)
            
            if status:
                query += " AND status = %s"
                params.append(status)
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            
            columns = [desc[0] for desc in cursor.description]
            results = []
            
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            
            cursor.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving evolution events: {e}")
            return []
    
    def propose_improvement(
        self,
        component: str,
        description: str,
        improvement_type: str,
        confidence: float,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Propose an improvement to the system.
        
        Args:
            component: Component to improve
            description: Description of the improvement
            improvement_type: Type of improvement
            confidence: Confidence score (0-1)
            metadata: Additional metadata
            
        Returns:
            Event ID if successful, None otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Evolution is disabled, cannot propose improvement")
            return None
        
        # Check if component is allowed to be modified
        if component not in self.config.allowed_modifications:
            if component in self.config.human_oversight_required:
                self.logger.info(
                    f"Component {component} requires human oversight, "
                    "creating proposal for review"
                )
            else:
                self.logger.warning(
                    f"Component {component} is not in allowed modifications list"
                )
                return None
        
        # Record metrics before
        metrics_before = self.metrics_collector.get_metric_stats(
            f"{component}_performance",
            window_minutes=60
        )
        
        # Create evolution event
        event_id = self.create_evolution_event(
            event_type=improvement_type,
            component=component,
            description=description,
            proposed_by="evolution_manager",
            status="proposed",
            metrics_before=metrics_before,
            metadata={
                **(metadata or {}),
                "confidence": confidence,
                "auto_apply": confidence >= self.config.auto_apply_threshold
            }
        )
        
        if event_id:
            self.logger.info(
                f"Proposed improvement for {component}: {description} "
                f"(confidence: {confidence:.2f})"
            )
        
        return event_id
    
    def apply_improvement(
        self,
        event_id: str,
        implementation_func: callable,
        **kwargs
    ) -> bool:
        """
        Apply an approved improvement.
        
        Args:
            event_id: ID of the evolution event
            implementation_func: Function to execute the improvement
            **kwargs: Arguments to pass to implementation function
            
        Returns:
            True if successful, False otherwise
        """
        if not self.is_enabled():
            self.logger.warning("Evolution is disabled, cannot apply improvement")
            return False
        
        try:
            # Update status to applying
            self.update_evolution_event(event_id, status="applying")
            
            # Start timer
            self.metrics_collector.start_timer(f"apply_improvement_{event_id}")
            
            # Execute improvement
            result = implementation_func(**kwargs)
            
            # End timer
            duration = self.metrics_collector.end_timer(
                f"apply_improvement_{event_id}",
                {"event_id": event_id}
            )
            
            if result:
                # Update status to applied
                self.update_evolution_event(
                    event_id,
                    status="applied",
                    metadata={"applied_at": datetime.now().isoformat(), "duration": duration}
                )
                self.logger.info(f"Successfully applied improvement: {event_id}")
                return True
            else:
                # Update status to failed
                self.update_evolution_event(event_id, status="rejected")
                self.logger.error(f"Failed to apply improvement: {event_id}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error applying improvement {event_id}: {e}")
            self.update_evolution_event(
                event_id,
                status="rejected",
                metadata={"error": str(e)}
            )
            return False
    
    def rollback_improvement(self, event_id: str) -> bool:
        """
        Rollback a previously applied improvement.
        
        Args:
            event_id: ID of the evolution event
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.update_evolution_event(event_id, status="rolled_back")
            self.logger.info(f"Rolled back improvement: {event_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error rolling back improvement {event_id}: {e}")
            return False
    
    def get_llm_response(self, prompt: str, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        Get a response from the local LLM.
        
        Args:
            prompt: Prompt to send to the LLM
            context: Additional context
            
        Returns:
            LLM response, or None if error
        """
        if not self.config.use_local_llm:
            self.logger.warning("Local LLM is disabled")
            return None
        
        try:
            # Assuming Ollama-compatible API
            response = requests.post(
                f"{self.config.local_llm_endpoint}/api/generate",
                json={
                    "model": "llama2",  # Default model
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response")
            else:
                self.logger.error(f"LLM request failed: {response.status_code}")
                return None
                
        except Exception as e:
            self.logger.error(f"Error getting LLM response: {e}")
            return None
    
    def __del__(self):
        """Close database connection on cleanup."""
        if self._conn and not self._conn.closed:
            self._conn.close()


class FlowstateEvolutionManager(EvolutionManager):
    """Wrapper that loads configuration from a file when provided."""

    def __init__(
        self,
        config: Optional[EvolutionConfig] = None,
        config_path: Optional[str] = None,
    ) -> None:
        resolved_config = config
        if resolved_config is None and config_path:
            with open(config_path, "r", encoding="utf-8") as config_file:
                config_data = json.load(config_file)
            resolved_config = EvolutionConfig.from_dict(config_data)
        super().__init__(config=resolved_config)

