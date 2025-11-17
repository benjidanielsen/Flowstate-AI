"""
Metrics Collector

Collects and stores performance metrics for analysis and anomaly detection.
"""

import logging
import time
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - exercised indirectly via tests
    import psycopg2
    from psycopg2.extras import Json
except ModuleNotFoundError:  # pragma: no cover - deterministic fallback
    psycopg2 = None  # type: ignore[assignment]

    def Json(value: Any) -> Any:  # type: ignore[misc]
        """Fallback Json adapter when psycopg2 isn't installed."""

        return value
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
        self._db_available = psycopg2 is not None
        self._memory_metrics: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self._memory_counter = 0

        if not self._db_available:
            self.logger.warning(
                "psycopg2 is not installed; falling back to in-memory metrics storage"
            )

    def _get_connection(self):
        """Get database connection."""
        if psycopg2 is None:
            raise RuntimeError("psycopg2 is required for database-backed metrics")

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
        record = self._build_record(metric_name, value, unit, context)

        if self._db_available:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                cursor.execute(
                    """
                    INSERT INTO performance_metrics
                    (metric_name, value, unit, component, context, timestamp)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    """,
                    (
                        metric_name,
                        value,
                        unit,
                        self.component_name,
                        Json(context or {}),
                        record["timestamp"],
                    )
                )

                conn.commit()
                cursor.close()

                self.logger.debug(
                    f"Recorded metric: {metric_name}={value}{unit} "
                    f"for component {self.component_name}"
                )
                return True

            except Exception as exc:
                self.logger.error(
                    "Error recording metric in database; switching to in-memory storage: %s",
                    exc,
                )
                self._db_available = False

        # Fallback to memory storage
        self._store_metric_in_memory(record)
        return True
    
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
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Retrieve metrics from the database.

        Args:
            metric_name: Filter by metric name (optional)
            since: Filter by timestamp (optional)
            limit: Maximum number of results

        Returns:
            Dictionary keyed by metric name where the value is a list of metric
            records ordered from oldest to newest
        """
        if self._db_available:
            try:
                conn = self._get_connection()
                cursor = conn.cursor()

                query = """
                    SELECT id, timestamp, metric_name, value, unit, component, context
                    FROM performance_metrics
                    WHERE component = %s
                """
                params: List[Any] = [self.component_name]

                if metric_name:
                    query += " AND metric_name = %s"
                    params.append(metric_name)

                if since:
                    query += " AND timestamp >= %s"
                    params.append(since)

                query += " ORDER BY timestamp DESC LIMIT %s"
                params.append(limit)

                cursor.execute(query, params)

                grouped: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
                for row in cursor.fetchall():
                    record = {
                        "id": str(row[0]),
                        "timestamp": row[1],
                        "metric_name": row[2],
                        "value": float(row[3]),
                        "unit": row[4],
                        "component": row[5],
                        "context": row[6],
                    }
                    grouped[record["metric_name"]].append(record)

                cursor.close()
                return {
                    name: sorted(records, key=lambda item: item["timestamp"])
                    for name, records in grouped.items()
                }

            except Exception as exc:
                self.logger.error("Error retrieving metrics from database: %s", exc)
                self._db_available = False

        return self._get_metrics_from_memory(metric_name, since, limit)
    
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
        records = metrics.get(metric_name, [])

        if not records:
            return None

        values = [m["value"] for m in records]
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
        records = metrics.get(metric_name, [])

        if not records:
            return None

        values = [m["value"] for m in records]
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
        if self._db_available:
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

            except Exception as exc:
                self.logger.error("Error cleaning up metrics: %s", exc)
                self._db_available = False

        cutoff_date = datetime.now() - timedelta(days=days)
        deleted = 0
        for metric_name, entries in list(self._memory_metrics.items()):
            remaining = [m for m in entries if m["timestamp"] >= cutoff_date]
            deleted += len(entries) - len(remaining)
            if remaining:
                self._memory_metrics[metric_name] = remaining
            else:
                del self._memory_metrics[metric_name]

        return deleted

    def __del__(self):
        """Close database connection on cleanup."""
        if self._conn and not getattr(self._conn, "closed", True):
            try:
                self._conn.close()
            except Exception:
                pass

    def _build_record(
        self,
        metric_name: str,
        value: float,
        unit: str,
        context: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        self._memory_counter += 1
        return {
            "id": f"mem-{self._memory_counter}",
            "timestamp": datetime.now(),
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "component": self.component_name,
            "context": context or {},
        }

    def _store_metric_in_memory(self, record: Dict[str, Any]) -> None:
        self._memory_metrics[record["metric_name"]].append(record)

    def _get_metrics_from_memory(
        self,
        metric_name: Optional[str],
        since: Optional[datetime],
        limit: int,
    ) -> Dict[str, List[Dict[str, Any]]]:
        results: Dict[str, List[Dict[str, Any]]] = {}
        keys = [metric_name] if metric_name else list(self._memory_metrics.keys())

        for key in keys:
            if key is None:
                continue

            entries = list(self._memory_metrics.get(key, []))
            if since:
                entries = [m for m in entries if m["timestamp"] >= since]

            if limit:
                entries = entries[-limit:]

            if entries:
                results[key] = entries

        return results

    def get_metric_values(
        self,
        metric_name: str,
        component: Optional[str] = None,
        limit: int = 100,
    ) -> List[float]:
        metrics = self.get_metrics(metric_name=metric_name, limit=limit)
        records = metrics.get(metric_name, [])
        return [record["value"] for record in records]

    def get_all_metric_components(self) -> List[Tuple[str, str]]:
        metrics = self.get_metrics()
        return [(metric_name, self.component_name) for metric_name in metrics.keys()]

