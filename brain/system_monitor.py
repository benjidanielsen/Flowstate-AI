"""
System Monitoring and Optimization Module for Flowstate-AI
Continuously monitors system performance, security, and health.
"""

import asyncio
import json
import logging
import psutil
import subprocess
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
import sqlite3
import redis
from .error_handler import with_retry, with_error_handling, CircuitBreaker, log_error_to_db, default_fallback_value

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SystemMonitor:
    """
    Comprehensive system monitoring and optimization module that tracks
    performance metrics, security status, and system health.
    """
    
    def __init__(self, db_path: str = "godmode-state.db", redis_host: str = "localhost"):
        """Initialize the system monitor."""
        self.db_path = Path(__file__).parent.parent / db_path
        self.redis = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)
        self.running = False
        self.monitoring_interval = 60  # 1 minute
        self.metrics_history: List[Dict[str, Any]] = []
        
        # Performance thresholds
        self.thresholds = {
            'cpu_percent': 80.0,
            'memory_percent': 85.0,
            'disk_percent': 90.0,
            'response_time_ms': 1000,
            'error_rate_percent': 5.0
        }
        
    @with_error_handling(fallback=default_fallback_value)
    def get_db_connection(self) -> sqlite3.Connection:

        """Get database connection."""
        conn = sqlite3.Connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn
        
    @with_error_handling(fallback=default_fallback_value)
    async def start(self):
        """Start the system monitoring."""
        self.running = True
        logger.info("System Monitor started")
        
        while self.running:
            try:
                await self.monitoring_cycle()
                await asyncio.sleep(self.monitoring_interval)
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {str(e)}")
                await asyncio.sleep(30)
                
    @with_error_handling(fallback=default_fallback_value)
    async def stop(self):
        """Stop the system monitoring."""
        self.running = False
        logger.info("System Monitor stopped")
        
    @with_error_handling(fallback=default_fallback_value)
    async def monitoring_cycle(self):
        """Execute one cycle of system monitoring."""
        metrics = await self.collect_metrics()
        
        # Store metrics
        await self.store_metrics(metrics)
        
        # Check for threshold violations
        alerts = self.check_thresholds(metrics)
        
        # Log alerts
        for alert in alerts:
            logger.warning(f"Threshold violation: {alert['metric']} = {alert['value']} (threshold: {alert['threshold']})")
            
        # Perform auto-optimization if needed
        if alerts:
            await self.auto_optimize(alerts)
            
    @with_error_handling(fallback=default_fallback_value)
    @with_retry(expected_exception=sqlite3.OperationalError)
    async def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect comprehensive system metrics.
        
        Returns:
            Dictionary containing all system metrics
        """
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'system': {},
            'application': {},
            'database': {},
            'security': {}
        }
        
        # System metrics
        metrics['system']['cpu_percent'] = psutil.cpu_percent(interval=1)
        metrics['system']['memory_percent'] = psutil.virtual_memory().percent
        metrics['system']['disk_percent'] = psutil.disk_usage('/').percent
        metrics['system']['network_connections'] = len(psutil.net_connections())
        
        # Application metrics
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'in_progress'")
        metrics['application']['active_tasks'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM agents WHERE status = 'active'")
        metrics['application']['active_agents'] = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks 
            WHERE status = 'failed' 
            AND updated_at >= datetime('now', '-1 hour')
        """)
        metrics['application']['recent_failures'] = cursor.fetchone()['count']
        
        conn.close()
        
        # Database metrics
        db_size = self.db_path.stat().st_size / (1024 * 1024)  # MB
        metrics['database']['size_mb'] = round(db_size, 2)
        
        # Security metrics (placeholder - would integrate with actual security tools)
        metrics['security']['last_scan'] = datetime.now().isoformat()
        metrics['security']['vulnerabilities_detected'] = 0
        
        return metrics
        
    @with_error_handling(fallback=default_fallback_value)
    async def store_metrics(self, metrics: Dict[str, Any]):
        """Store metrics in Redis for historical analysis."""
        try:
            key = f"metrics:{datetime.now().timestamp()}"
            self.redis.set(key, json.dumps(metrics))
            self.redis.expire(key, 86400 * 7)  # Keep for 7 days
            
            # Also keep in memory for quick access
            self.metrics_history.append(metrics)
            if len(self.metrics_history) > 1000:
                self.metrics_history.pop(0)
        except Exception as e:
            logger.error(f"Error storing metrics: {str(e)}")
            
    @with_error_handling(fallback=default_fallback_value)
    def check_thresholds(self, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Check if any metrics exceed defined thresholds.
        
        Returns:
            List of threshold violations
        """
        alerts = []
        
        # Check CPU
        cpu_percent = metrics['system'].get('cpu_percent', 0)
        if cpu_percent > self.thresholds['cpu_percent']:
            alerts.append({
                'metric': 'cpu_percent',
                'value': cpu_percent,
                'threshold': self.thresholds['cpu_percent'],
                'severity': 'warning'
            })
        
        # Check memory
        memory_percent = metrics['system'].get('memory_percent', 0)
        if memory_percent > self.thresholds['memory_percent']:
            alerts.append({
                'metric': 'memory_percent',
                'value': memory_percent,
                'threshold': self.thresholds['memory_percent'],
                'severity': 'warning'
            })
        
        # Check disk
        disk_percent = metrics['system'].get('disk_percent', 0)
        if disk_percent > self.thresholds['disk_percent']:
            alerts.append({
                'metric': 'disk_percent',
                'value': disk_percent,
                'threshold': self.thresholds['disk_percent'],
                'severity': 'critical'
            })
        
        return alerts
        
    @with_error_handling(fallback=default_fallback_value)
    async def auto_optimize(self, alerts: List[Dict[str, Any]]):
        """
        Automatically optimize system based on alerts.
        
        Args:
            alerts: List of threshold violations
        """
        for alert in alerts:
            metric = alert['metric']
            
            if metric == 'memory_percent':
                logger.info("Attempting memory optimization...")
                # Clear Redis cache if memory is high
                try:
                    # Get all keys older than 1 day
                    for key in self.redis.scan_iter():
                        ttl = self.redis.ttl(key)
                        if ttl > 86400:  # More than 1 day
                            self.redis.delete(key)
                    logger.info("Cleared old Redis cache entries")
                except Exception as e:
                    logger.error(f"Error optimizing memory: {str(e)}")
                    
            elif metric == 'disk_percent':
                logger.info("Attempting disk optimization...")
                # Clean up old log files
                try:
                    log_dir = Path(__file__).parent.parent / "logs"
                    if log_dir.exists():
                        for log_file in log_dir.glob("*.log"):
                            if log_file.stat().st_mtime < (datetime.now() - timedelta(days=30)).timestamp():
                                log_file.unlink()
                                logger.info(f"Deleted old log file: {log_file.name}")
                except Exception as e:
                    logger.error(f"Error optimizing disk: {str(e)}")
                    
    @with_error_handling(fallback=default_fallback_value)
    def get_health_status(self) -> Dict[str, Any]:
        """
        Get overall system health status.
        
        Returns:
            Dictionary with health status and metrics
        """
        if not self.metrics_history:
            return {'status': 'unknown', 'message': 'No metrics collected yet'}
        
        latest_metrics = self.metrics_history[-1]
        
        # Calculate health score (0-100)
        health_score = 100
        
        # Deduct points for high resource usage
        cpu_percent = latest_metrics['system'].get('cpu_percent', 0)
        if cpu_percent > 80:
            health_score -= (cpu_percent - 80) * 2
        
        memory_percent = latest_metrics['system'].get('memory_percent', 0)
        if memory_percent > 85:
            health_score -= (memory_percent - 85) * 2
        
        disk_percent = latest_metrics['system'].get('disk_percent', 0)
        if disk_percent > 90:
            health_score -= (disk_percent - 90) * 3
        
        # Deduct points for recent failures
        recent_failures = latest_metrics['application'].get('recent_failures', 0)
        health_score -= recent_failures * 5
        
        health_score = max(0, min(100, health_score))
        
        # Determine status
        if health_score >= 90:
            status = 'excellent'
        elif health_score >= 75:
            status = 'good'
        elif health_score >= 50:
            status = 'fair'
        else:
            status = 'poor'
        
        return {
            'status': status,
            'health_score': round(health_score, 1),
            'metrics': latest_metrics,
            'timestamp': datetime.now().isoformat()
        }
        
    @with_error_handling(fallback=default_fallback_value)
    def get_performance_trends(self, hours: int = 24) -> Dict[str, Any]:
        """
        Analyze performance trends over a specified period.
        
        Args:
            hours: Number of hours to analyze
            
        Returns:
            Dictionary with trend analysis
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        # Filter metrics within time window
        recent_metrics = [
            m for m in self.metrics_history
            if datetime.fromisoformat(m['timestamp']) >= cutoff_time
        ]
        
        if not recent_metrics:
            return {'message': f'No metrics in the last {hours} hours'}
        
        # Calculate averages
        avg_cpu = sum(m['system'].get('cpu_percent', 0) for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m['system'].get('memory_percent', 0) for m in recent_metrics) / len(recent_metrics)
        avg_disk = sum(m['system'].get('disk_percent', 0) for m in recent_metrics) / len(recent_metrics)
        
        # Calculate trends (comparing first half vs second half)
        mid_point = len(recent_metrics) // 2
        first_half = recent_metrics[:mid_point]
        second_half = recent_metrics[mid_point:]
        
        if first_half and second_half:
            cpu_trend = (sum(m['system'].get('cpu_percent', 0) for m in second_half) / len(second_half)) - \
                       (sum(m['system'].get('cpu_percent', 0) for m in first_half) / len(first_half))
            
            memory_trend = (sum(m['system'].get('memory_percent', 0) for m in second_half) / len(second_half)) - \
                          (sum(m['system'].get('memory_percent', 0) for m in first_half) / len(first_half))
        else:
            cpu_trend = 0
            memory_trend = 0
        
        return {
            'period_hours': hours,
            'averages': {
                'cpu_percent': round(avg_cpu, 2),
                'memory_percent': round(avg_memory, 2),
                'disk_percent': round(avg_disk, 2)
            },
            'trends': {
                'cpu': 'increasing' if cpu_trend > 5 else 'decreasing' if cpu_trend < -5 else 'stable',
                'memory': 'increasing' if memory_trend > 5 else 'decreasing' if memory_trend < -5 else 'stable'
            },
            'data_points': len(recent_metrics),
            'timestamp': datetime.now().isoformat()
        }


async def main():
    """Main function to run the system monitor."""
    monitor = SystemMonitor()
    
    try:
        await monitor.start()
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
        await monitor.stop()


if __name__ == "__main__":
    asyncio.run(main())
