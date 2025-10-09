"""
Anomaly Detection - Proactive monitoring and issue identification

This module implements anomaly detection for system metrics, performance indicators,
and behavioral patterns to enable early detection of potential issues.
"""

import asyncio
import logging
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from collections import deque
from enum import Enum

logger = logging.getLogger(__name__)


class AnomalySeverity(Enum):
    """Severity levels for detected anomalies"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Anomaly:
    """Represents a detected anomaly"""
    anomaly_id: str
    metric_name: str
    severity: AnomalySeverity
    value: float
    expected_range: Tuple[float, float]
    deviation: float
    timestamp: str
    context: Dict[str, Any]
    resolved: bool = False
    resolved_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        data = asdict(self)
        data["severity"] = self.severity.value
        return data


@dataclass
class MetricStats:
    """Statistical summary of a metric"""
    metric_name: str
    count: int
    mean: float
    std: float
    min: float
    max: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float
    percentile_99: float
    
    def get_expected_range(self, sigma: float = 3.0) -> Tuple[float, float]:
        """Get expected range based on standard deviations"""
        return (
            self.mean - sigma * self.std,
            self.mean + sigma * self.std
        )


class AnomalyDetector:
    """
    Anomaly detection system for proactive monitoring
    
    Uses statistical methods and machine learning to detect unusual patterns
    in system metrics and performance indicators.
    """
    
    def __init__(
        self,
        window_size: int = 1000,
        detection_threshold: float = 3.0,
        min_samples: int = 30,
        alert_cooldown: int = 300  # seconds
    ):
        """
        Initialize Anomaly Detector
        
        Args:
            window_size: Number of samples to keep for each metric
            detection_threshold: Number of standard deviations for anomaly
            min_samples: Minimum samples needed before detection
            alert_cooldown: Cooldown period between alerts for same metric
        """
        self.window_size = window_size
        self.detection_threshold = detection_threshold
        self.min_samples = min_samples
        self.alert_cooldown = alert_cooldown
        
        # Metric storage
        self.metrics: Dict[str, deque] = {}
        self.metric_stats: Dict[str, MetricStats] = {}
        
        # Anomaly tracking
        self.anomalies: List[Anomaly] = []
        self.last_alert_time: Dict[str, datetime] = {}
        
        # Detection models (for ML-based detection)
        self.models: Dict[str, Any] = {}
        
        logger.info(f"Anomaly Detector initialized with window_size={window_size}, "
                   f"threshold={detection_threshold}")
    
    async def record_metric(
        self,
        metric_name: str,
        value: float,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[Anomaly]:
        """
        Record a metric value and check for anomalies
        
        Args:
            metric_name: Name of the metric
            value: Metric value
            context: Additional context information
            
        Returns:
            Anomaly if detected, None otherwise
        """
        # Initialize metric storage if needed
        if metric_name not in self.metrics:
            self.metrics[metric_name] = deque(maxlen=self.window_size)
        
        # Record value
        self.metrics[metric_name].append({
            "value": value,
            "timestamp": datetime.utcnow().isoformat(),
            "context": context or {}
        })
        
        # Update statistics
        await self._update_stats(metric_name)
        
        # Check for anomalies
        anomaly = await self._detect_anomaly(metric_name, value, context or {})
        
        if anomaly:
            self.anomalies.append(anomaly)
            logger.warning(f"Anomaly detected: {anomaly.metric_name} = {anomaly.value:.2f} "
                         f"(expected: {anomaly.expected_range}, severity: {anomaly.severity.value})")
        
        return anomaly
    
    async def _update_stats(self, metric_name: str) -> None:
        """Update statistical summary for a metric"""
        values = [item["value"] for item in self.metrics[metric_name]]
        
        if len(values) < 2:
            return
        
        values_array = np.array(values)
        
        self.metric_stats[metric_name] = MetricStats(
            metric_name=metric_name,
            count=len(values),
            mean=float(np.mean(values_array)),
            std=float(np.std(values_array)),
            min=float(np.min(values_array)),
            max=float(np.max(values_array)),
            percentile_25=float(np.percentile(values_array, 25)),
            percentile_50=float(np.percentile(values_array, 50)),
            percentile_75=float(np.percentile(values_array, 75)),
            percentile_95=float(np.percentile(values_array, 95)),
            percentile_99=float(np.percentile(values_array, 99))
        )
    
    async def _detect_anomaly(
        self,
        metric_name: str,
        value: float,
        context: Dict[str, Any]
    ) -> Optional[Anomaly]:
        """Detect if a value is anomalous"""
        # Need minimum samples
        if len(self.metrics[metric_name]) < self.min_samples:
            return None
        
        # Check alert cooldown
        if metric_name in self.last_alert_time:
            time_since_last = (datetime.utcnow() - self.last_alert_time[metric_name]).total_seconds()
            if time_since_last < self.alert_cooldown:
                return None
        
        stats = self.metric_stats.get(metric_name)
        if not stats:
            return None
        
        # Statistical anomaly detection (Z-score)
        if stats.std > 0:
            z_score = abs((value - stats.mean) / stats.std)
            
            if z_score > self.detection_threshold:
                # Determine severity
                if z_score > self.detection_threshold * 2:
                    severity = AnomalySeverity.CRITICAL
                elif z_score > self.detection_threshold * 1.5:
                    severity = AnomalySeverity.HIGH
                elif z_score > self.detection_threshold * 1.2:
                    severity = AnomalySeverity.MEDIUM
                else:
                    severity = AnomalySeverity.LOW
                
                expected_range = stats.get_expected_range(self.detection_threshold)
                
                anomaly = Anomaly(
                    anomaly_id=f"{metric_name}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                    metric_name=metric_name,
                    severity=severity,
                    value=value,
                    expected_range=expected_range,
                    deviation=z_score,
                    timestamp=datetime.utcnow().isoformat(),
                    context=context
                )
                
                self.last_alert_time[metric_name] = datetime.utcnow()
                
                return anomaly
        
        return None
    
    async def get_metric_stats(self, metric_name: str) -> Optional[MetricStats]:
        """Get statistical summary for a metric"""
        return self.metric_stats.get(metric_name)
    
    async def get_recent_anomalies(
        self,
        metric_name: Optional[str] = None,
        severity: Optional[AnomalySeverity] = None,
        hours: int = 24,
        include_resolved: bool = False
    ) -> List[Anomaly]:
        """
        Get recent anomalies
        
        Args:
            metric_name: Filter by metric name
            severity: Filter by severity
            hours: Time window in hours
            include_resolved: Include resolved anomalies
            
        Returns:
            List of anomalies
        """
        cutoff_time = datetime.utcnow() - timedelta(hours=hours)
        
        filtered = []
        for anomaly in self.anomalies:
            anomaly_time = datetime.fromisoformat(anomaly.timestamp)
            
            # Time filter
            if anomaly_time < cutoff_time:
                continue
            
            # Metric filter
            if metric_name and anomaly.metric_name != metric_name:
                continue
            
            # Severity filter
            if severity and anomaly.severity != severity:
                continue
            
            # Resolved filter
            if not include_resolved and anomaly.resolved:
                continue
            
            filtered.append(anomaly)
        
        return sorted(filtered, key=lambda a: a.timestamp, reverse=True)
    
    async def resolve_anomaly(self, anomaly_id: str) -> bool:
        """Mark an anomaly as resolved"""
        for anomaly in self.anomalies:
            if anomaly.anomaly_id == anomaly_id:
                anomaly.resolved = True
                anomaly.resolved_at = datetime.utcnow().isoformat()
                logger.info(f"Resolved anomaly: {anomaly_id}")
                return True
        
        return False
    
    async def get_anomaly_summary(self) -> Dict[str, Any]:
        """Get summary of anomalies"""
        recent = await self.get_recent_anomalies(hours=24)
        
        by_severity = {
            AnomalySeverity.LOW: 0,
            AnomalySeverity.MEDIUM: 0,
            AnomalySeverity.HIGH: 0,
            AnomalySeverity.CRITICAL: 0
        }
        
        by_metric = {}
        unresolved_count = 0
        
        for anomaly in recent:
            by_severity[anomaly.severity] += 1
            by_metric[anomaly.metric_name] = by_metric.get(anomaly.metric_name, 0) + 1
            if not anomaly.resolved:
                unresolved_count += 1
        
        return {
            "total_24h": len(recent),
            "unresolved": unresolved_count,
            "by_severity": {k.value: v for k, v in by_severity.items()},
            "by_metric": by_metric,
            "most_affected_metrics": sorted(
                by_metric.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
        }
    
    async def train_ml_detector(
        self,
        metric_name: str,
        model_type: str = "isolation_forest"
    ) -> bool:
        """
        Train ML-based anomaly detector for a metric
        
        Args:
            metric_name: Metric to train on
            model_type: Type of ML model ("isolation_forest", "autoencoder")
            
        Returns:
            Success status
        """
        if metric_name not in self.metrics or len(self.metrics[metric_name]) < 100:
            logger.warning(f"Insufficient data for ML training: {metric_name}")
            return False
        
        try:
            from sklearn.ensemble import IsolationForest
            
            # Prepare training data
            values = np.array([item["value"] for item in self.metrics[metric_name]]).reshape(-1, 1)
            
            if model_type == "isolation_forest":
                model = IsolationForest(
                    contamination=0.1,
                    random_state=42,
                    n_estimators=100
                )
                model.fit(values)
                
                self.models[metric_name] = {
                    "type": model_type,
                    "model": model,
                    "trained_at": datetime.utcnow().isoformat()
                }
                
                logger.info(f"Trained ML detector for {metric_name}: {model_type}")
                return True
            
            else:
                logger.warning(f"Unsupported model type: {model_type}")
                return False
        
        except Exception as e:
            logger.error(f"Failed to train ML detector: {str(e)}", exc_info=True)
            return False
    
    async def predict_ml_anomaly(
        self,
        metric_name: str,
        value: float
    ) -> Tuple[bool, float]:
        """
        Use ML model to predict if value is anomalous
        
        Args:
            metric_name: Metric name
            value: Value to check
            
        Returns:
            (is_anomaly, anomaly_score)
        """
        if metric_name not in self.models:
            return False, 0.0
        
        try:
            model_info = self.models[metric_name]
            model = model_info["model"]
            
            prediction = model.predict([[value]])
            score = model.score_samples([[value]])[0]
            
            is_anomaly = prediction[0] == -1
            
            return is_anomaly, abs(score)
        
        except Exception as e:
            logger.error(f"ML prediction failed: {str(e)}")
            return False, 0.0

