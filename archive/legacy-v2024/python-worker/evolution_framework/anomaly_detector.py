"""
Anomaly Detector

Detects performance anomalies using statistical methods.
"""

import logging
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from .metrics_collector import MetricsCollector


class AnomalyDetector:
    """Detects anomalies in system metrics using statistical methods."""
    
    def __init__(
        self,
        metrics_collector: MetricsCollector,
        window_size: int = 100,
        threshold_std_dev: float = 2.0
    ):
        """
        Initialize the anomaly detector.
        
        Args:
            metrics_collector: Metrics collector instance
            window_size: Number of data points to consider for analysis
            threshold_std_dev: Z-score threshold for anomaly detection
        """
        self.metrics_collector = metrics_collector
        self.window_size = window_size
        self.threshold_std_dev = threshold_std_dev
        self.logger = logging.getLogger("anomaly_detector")
        
        # Track detected anomalies
        self.anomaly_history = []
    
    def detect_anomaly(
        self,
        metric_name: str,
        component: str = "system"
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Detect anomalies in a specific metric using Z-score method.
        
        Args:
            metric_name: Name of the metric to analyze
            component: Component name for filtering
            
        Returns:
            Tuple of (is_anomaly, anomaly_details)
        """
        try:
            # Get recent metric values
            stats = self.metrics_collector.get_metric_stats(
                metric_name,
                component,
                limit=self.window_size
            )
            
            if not stats or stats['count'] < self.window_size:
                self.logger.debug(
                    f"Not enough data for anomaly detection: "
                    f"{metric_name} ({stats['count'] if stats else 0}/{self.window_size})"
                )
                return False, None
            
            # Get all values for statistical analysis
            values = self.metrics_collector.get_metric_values(
                metric_name,
                component,
                limit=self.window_size
            )
            
            if not values:
                return False, None
            
            # Calculate statistics
            mean = np.mean(values)
            std_dev = np.std(values)
            latest_value = values[-1]
            
            # Avoid division by zero
            if std_dev == 0:
                self.logger.debug(f"Zero standard deviation for {metric_name}")
                return False, None
            
            # Calculate Z-score
            z_score = (latest_value - mean) / std_dev
            
            # Check if anomaly
            if abs(z_score) > self.threshold_std_dev:
                anomaly_details = {
                    "metric_name": metric_name,
                    "component": component,
                    "latest_value": latest_value,
                    "mean": mean,
                    "std_dev": std_dev,
                    "z_score": z_score,
                    "threshold": self.threshold_std_dev,
                    "severity": self._calculate_severity(abs(z_score)),
                    "timestamp": datetime.now().isoformat()
                }
                
                self.logger.warning(
                    f"Anomaly detected: {metric_name} = {latest_value:.2f} "
                    f"(mean: {mean:.2f}, std: {std_dev:.2f}, z-score: {z_score:.2f})"
                )
                
                # Record anomaly
                self.anomaly_history.append(anomaly_details)
                
                return True, anomaly_details
            
            return False, None
        
        except Exception as e:
            self.logger.error(f"Error detecting anomaly for {metric_name}: {e}")
            return False, None
    
    def _calculate_severity(self, z_score: float) -> str:
        """
        Calculate severity level based on Z-score.
        
        Args:
            z_score: Absolute Z-score value
            
        Returns:
            Severity level string
        """
        if z_score >= 4.0:
            return "critical"
        elif z_score >= 3.0:
            return "high"
        elif z_score >= 2.5:
            return "medium"
        else:
            return "low"
    
    def monitor_all_metrics(self) -> List[Dict[str, Any]]:
        """
        Monitor all tracked metrics for anomalies.
        
        Returns:
            List of detected anomalies
        """
        self.logger.info("Monitoring all metrics for anomalies")
        anomalies = []
        
        # Get all unique metric/component combinations
        metric_components = self.metrics_collector.get_all_metric_components()
        
        for metric_name, component in metric_components:
            is_anomaly, details = self.detect_anomaly(metric_name, component)
            if is_anomaly and details:
                anomalies.append(details)
        
        if anomalies:
            self.logger.warning(f"Detected {len(anomalies)} anomalies")
        else:
            self.logger.info("No anomalies detected")
        
        return anomalies
    
    def detect_trend_anomaly(
        self,
        metric_name: str,
        component: str = "system",
        trend_window: int = 10
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Detect anomalies in metric trends using linear regression.
        
        Args:
            metric_name: Name of the metric to analyze
            component: Component name for filtering
            trend_window: Number of recent points to analyze for trend
            
        Returns:
            Tuple of (is_anomaly, anomaly_details)
        """
        try:
            # Get recent metric values
            values = self.metrics_collector.get_metric_values(
                metric_name,
                component,
                limit=self.window_size
            )
            
            if not values or len(values) < trend_window:
                return False, None
            
            # Get recent trend
            recent_values = values[-trend_window:]
            x = np.arange(len(recent_values))
            
            # Calculate linear regression
            coefficients = np.polyfit(x, recent_values, 1)
            slope = coefficients[0]
            
            # Get historical trend
            if len(values) > trend_window * 2:
                historical_values = values[:-trend_window]
                historical_x = np.arange(len(historical_values))
                historical_coefficients = np.polyfit(historical_x, historical_values, 1)
                historical_slope = historical_coefficients[0]
                
                # Compare slopes
                if historical_slope != 0:
                    slope_change = abs((slope - historical_slope) / historical_slope)
                    
                    # Detect significant trend change (>50% change)
                    if slope_change > 0.5:
                        anomaly_details = {
                            "metric_name": metric_name,
                            "component": component,
                            "type": "trend",
                            "recent_slope": slope,
                            "historical_slope": historical_slope,
                            "slope_change": slope_change,
                            "severity": "high" if slope_change > 1.0 else "medium",
                            "timestamp": datetime.now().isoformat()
                        }
                        
                        self.logger.warning(
                            f"Trend anomaly detected: {metric_name} slope changed by "
                            f"{slope_change:.2%}"
                        )
                        
                        self.anomaly_history.append(anomaly_details)
                        return True, anomaly_details
            
            return False, None
        
        except Exception as e:
            self.logger.error(f"Error detecting trend anomaly for {metric_name}: {e}")
            return False, None
    
    def detect_spike_anomaly(
        self,
        metric_name: str,
        component: str = "system",
        spike_threshold: float = 3.0
    ) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """
        Detect sudden spikes or drops in metric values.
        
        Args:
            metric_name: Name of the metric to analyze
            component: Component name for filtering
            spike_threshold: Multiplier threshold for spike detection
            
        Returns:
            Tuple of (is_anomaly, anomaly_details)
        """
        try:
            # Get recent metric values
            values = self.metrics_collector.get_metric_values(
                metric_name,
                component,
                limit=10
            )
            
            if not values or len(values) < 3:
                return False, None
            
            # Compare latest value to recent average
            latest_value = values[-1]
            recent_avg = np.mean(values[:-1])
            
            if recent_avg == 0:
                return False, None
            
            # Calculate ratio
            ratio = abs(latest_value / recent_avg)
            
            # Detect spike
            if ratio > spike_threshold or ratio < (1 / spike_threshold):
                spike_type = "spike" if ratio > spike_threshold else "drop"
                
                anomaly_details = {
                    "metric_name": metric_name,
                    "component": component,
                    "type": spike_type,
                    "latest_value": latest_value,
                    "recent_average": recent_avg,
                    "ratio": ratio,
                    "threshold": spike_threshold,
                    "severity": "high" if ratio > spike_threshold * 2 else "medium",
                    "timestamp": datetime.now().isoformat()
                }
                
                self.logger.warning(
                    f"{spike_type.capitalize()} detected: {metric_name} = {latest_value:.2f} "
                    f"(recent avg: {recent_avg:.2f}, ratio: {ratio:.2f})"
                )
                
                self.anomaly_history.append(anomaly_details)
                return True, anomaly_details
            
            return False, None
        
        except Exception as e:
            self.logger.error(f"Error detecting spike anomaly for {metric_name}: {e}")
            return False, None
    
    def comprehensive_anomaly_check(
        self,
        metric_name: str,
        component: str = "system"
    ) -> List[Dict[str, Any]]:
        """
        Run all anomaly detection methods on a metric.
        
        Args:
            metric_name: Name of the metric to analyze
            component: Component name for filtering
            
        Returns:
            List of all detected anomalies
        """
        anomalies = []
        
        # Z-score anomaly
        is_anomaly, details = self.detect_anomaly(metric_name, component)
        if is_anomaly and details:
            anomalies.append(details)
        
        # Trend anomaly
        is_anomaly, details = self.detect_trend_anomaly(metric_name, component)
        if is_anomaly and details:
            anomalies.append(details)
        
        # Spike anomaly
        is_anomaly, details = self.detect_spike_anomaly(metric_name, component)
        if is_anomaly and details:
            anomalies.append(details)
        
        return anomalies
    
    def get_anomaly_report(
        self,
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        Generate a report of anomalies detected in the specified time window.
        
        Args:
            hours: Number of hours to look back
            
        Returns:
            Anomaly report dictionary
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_anomalies = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        # Group by severity
        by_severity = {}
        for anomaly in recent_anomalies:
            severity = anomaly.get('severity', 'unknown')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(anomaly)
        
        # Group by metric
        by_metric = {}
        for anomaly in recent_anomalies:
            metric = anomaly['metric_name']
            if metric not in by_metric:
                by_metric[metric] = []
            by_metric[metric].append(anomaly)
        
        return {
            "time_window_hours": hours,
            "total_anomalies": len(recent_anomalies),
            "by_severity": {
                severity: len(anomalies)
                for severity, anomalies in by_severity.items()
            },
            "by_metric": {
                metric: len(anomalies)
                for metric, anomalies in by_metric.items()
            },
            "recent_anomalies": recent_anomalies[-10:],  # Last 10
            "generated_at": datetime.now().isoformat()
        }
    
    def clear_anomaly_history(self, hours: Optional[int] = None) -> int:
        """
        Clear anomaly history older than specified hours.
        
        Args:
            hours: Number of hours to retain (None = clear all)
            
        Returns:
            Number of anomalies cleared
        """
        if hours is None:
            count = len(self.anomaly_history)
            self.anomaly_history = []
            self.logger.info(f"Cleared all {count} anomalies from history")
            return count
        
        cutoff_time = datetime.now() - timedelta(hours=hours)
        original_count = len(self.anomaly_history)
        
        self.anomaly_history = [
            a for a in self.anomaly_history
            if datetime.fromisoformat(a['timestamp']) > cutoff_time
        ]
        
        cleared_count = original_count - len(self.anomaly_history)
        self.logger.info(f"Cleared {cleared_count} anomalies older than {hours} hours")
        
        return cleared_count

