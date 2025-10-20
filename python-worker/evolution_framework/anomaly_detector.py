"""Simplified anomaly detector without external dependencies."""
from __future__ import annotations

import logging
from math import sqrt
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

from .metrics_collector import MetricsCollector


class AnomalyDetector:
    """Detect anomalies using a basic Z-score implementation."""

    def __init__(
        self,
        metrics_collector: MetricsCollector,
        window_size: int = 100,
        threshold_std_dev: float = 2.0,
    ) -> None:
        self.metrics_collector = metrics_collector
        self.window_size = window_size
        self.threshold_std_dev = threshold_std_dev
        self.logger = logging.getLogger("anomaly_detector")
        self.anomaly_history: List[Dict[str, Any]] = []

    def detect_anomaly(self, metric_name: str, component: str = "system") -> Tuple[bool, Optional[Dict[str, Any]]]:
        stats = self.metrics_collector.get_metric_stats(metric_name, component, limit=self.window_size)
        if not stats or stats["count"] < self.window_size:
            self.logger.debug(
                "Not enough data for anomaly detection: %s (%s/%s)",
                metric_name,
                stats["count"] if stats else 0,
                self.window_size,
            )
            return False, None

        values = self.metrics_collector.get_metric_values(metric_name, component, limit=self.window_size)
        if not values:
            return False, None

        mean = sum(values) / len(values)
        variance = sum((value - mean) ** 2 for value in values) / len(values)
        std_dev = sqrt(variance)
        latest_value = values[-1]

        if std_dev == 0:
            self.logger.debug("Zero standard deviation for %s", metric_name)
            return False, None

        z_score = (latest_value - mean) / std_dev
        if abs(z_score) <= self.threshold_std_dev:
            return False, None

        anomaly_details = {
            "metric_name": metric_name,
            "component": component,
            "latest_value": latest_value,
            "mean": mean,
            "std_dev": std_dev,
            "z_score": z_score,
            "threshold": self.threshold_std_dev,
            "severity": self._calculate_severity(abs(z_score)),
            "timestamp": datetime.now().isoformat(),
        }
        self.anomaly_history.append(anomaly_details)
        self.logger.warning(
            "Anomaly detected: %s = %.2f (mean %.2f, std %.2f, z-score %.2f)",
            metric_name,
            latest_value,
            mean,
            std_dev,
            z_score,
        )
        return True, anomaly_details

    def _calculate_severity(self, z_score: float) -> str:
        if z_score >= 4.0:
            return "critical"
        if z_score >= 3.0:
            return "high"
        if z_score >= 2.5:
            return "medium"
        return "low"

    def monitor_all_metrics(self) -> List[Dict[str, Any]]:
        anomalies: List[Dict[str, Any]] = []
        for metric_name, component in self.metrics_collector.get_all_metric_components():
            is_anomaly, details = self.detect_anomaly(metric_name, component)
            if is_anomaly and details:
                anomalies.append(details)
        if anomalies:
            self.logger.warning("Detected %s anomalies", len(anomalies))
        return anomalies

    def get_anomaly_history(self) -> List[Dict[str, Any]]:
        return list(self.anomaly_history)
