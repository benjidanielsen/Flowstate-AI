"""
Metrics Collector

Collects and stores performance metrics for analysis and anomaly detection.
"""

import logging
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import psycopg2
from psycopg2.extras import Json
from .config import EvolutionConfig


class MetricsCollector:
    """Collects and stores performance metrics."""
    
    def __init__(self, component_name: str, config: Optional[EvolutionConfig] = None):
        """
        Initialize the metrics collector.
        
        Args:
            component_name: Name of the component collecting metrics
            config: Evolution framework configuration
        """
        self.component_name = component_name
        self.config = config or EvolutionConfig()
        self.logger = logging.getLogger(f"metrics_collector.{component_name}")
        self.timers: Dict[str, float] = {}
        self._conn = None
        
    def _get_connection(self):
        """Get database connection."""
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(self.config.database_url)
        return self._conn
    
    def record_metric(
        self,
        metric_name: str,
        value: float,
        unit: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Record a performance metric.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            unit: Unit of measurement
            context: Additional context data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cursor.execute(
                """
                INSERT INTO performance_metrics 
                (metric_name, value, unit, component, context)
                VALUES (%s, %s, %s, %s, %s)
                """,
                (metric_name, value, unit, self.component_name, Json(context or {}))
            )
            
            conn.commit()
            cursor.close()
            
            self.logger.debug(
                f"Recorded metric: {metric_name}={value}{unit} "
                f"for component {self.component_name}"
            )
            return True
            
        except Exception as e:
            self.logger.error(f"Error recording metric: {e}")
            return False
    
    def start_timer(self, timer_name: str) -> None:
        """
        Start a timer for measuring duration.
        
        Args:
            timer_name: Name of the timer
        """
        self.timers[timer_name] = time.time()
        self.logger.debug(f"Started timer: {timer_name}")
    
    def end_timer(self, timer_name: str, context: Optional[Dict[str, Any]] = None) -> Optional[float]:
        """
        End a timer and record the duration.
        
        Args:
            timer_name: Name of the timer
            context: Additional context data
            
        Returns:
            Duration in seconds, or None if timer not found
        """
        if timer_name not in self.timers:
            self.logger.warning(f"Timer not found: {timer_name}")
            return None
        
        start_time = self.timers.pop(timer_name)
        duration = time.time() - start_time
        
        self.record_metric(
            f"{timer_name}_duration",
            duration,
            "seconds",
            context
        )
        
        self.logger.debug(f"Timer {timer_name} ended: {duration:.2f}s")
        return duration
    
    def get_metrics(
        self,
        metric_name: Optional[str] = None,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Retrieve metrics from the database.
        
        Args:
            metric_name: Filter by metric name (optional)
            since: Filter by timestamp (optional)
            limit: Maximum number of results
            
        Returns:
            List of metric records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            query = """
                SELECT id, timestamp, metric_name, value, unit, component, context
                FROM performance_metrics
                WHERE component = %s
            """
            params = [self.component_name]
            
            if metric_name:
                query += " AND metric_name = %s"
                params.append(metric_name)
            
            if since:
                query += " AND timestamp >= %s"
                params.append(since)
            
            query += " ORDER BY timestamp DESC LIMIT %s"
            params.append(limit)
            
            cursor.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append({
                    "id": str(row[0]),
                    "timestamp": row[1],
                    "metric_name": row[2],
                    "value": float(row[3]),
                    "unit": row[4],
                    "component": row[5],
                    "context": row[6]
                })
            
            cursor.close()
            return results
            
        except Exception as e:
            self.logger.error(f"Error retrieving metrics: {e}")
            return []
    
    def get_metric_average(
        self,
        metric_name: str,
        window_minutes: int = 60
    ) -> Optional[float]:
        """
        Get the average value of a metric over a time window.
        
        Args:
            metric_name: Name of the metric
            window_minutes: Time window in minutes
            
        Returns:
            Average value, or None if no data
        """
        since = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(metric_name=metric_name, since=since)
        
        if not metrics:
            return None
        
        values = [m["value"] for m in metrics]
        return sum(values) / len(values)
    
    def get_metric_stats(
        self,
        metric_name: str,
        window_minutes: int = 60
    ) -> Optional[Dict[str, float]]:
        """
        Get statistical summary of a metric over a time window.
        
        Args:
            metric_name: Name of the metric
            window_minutes: Time window in minutes
            
        Returns:
            Dictionary with min, max, avg, count
        """
        since = datetime.now() - timedelta(minutes=window_minutes)
        metrics = self.get_metrics(metric_name=metric_name, since=since)
        
        if not metrics:
            return None
        
        values = [m["value"] for m in metrics]
        return {
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "count": len(values)
        }
    
    def cleanup_old_metrics(self, days: int = 90) -> int:
        """
        Delete metrics older than specified days.
        
        Args:
            days: Number of days to retain
            
        Returns:
            Number of records deleted
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            
            cutoff_date = datetime.now() - timedelta(days=days)
            
            cursor.execute(
                """
                DELETE FROM performance_metrics
                WHERE component = %s AND timestamp < %s
                """,
                (self.component_name, cutoff_date)
            )
            
            deleted_count = cursor.rowcount
            conn.commit()
            cursor.close()
            
            self.logger.info(f"Cleaned up {deleted_count} old metrics")
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up metrics: {e}")
            return 0
    
    def __del__(self):
        """Close database connection on cleanup."""
        if self._conn and not self._conn.closed:
            self._conn.close()

