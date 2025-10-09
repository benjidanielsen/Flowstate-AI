import logging
import numpy as np
from collections import deque
from metrics_collector import MetricsCollector

class AnomalyDetector:
    def __init__(self, metrics_collector: MetricsCollector, window_size=10, threshold_std_dev=2.0):
        self.metrics_collector = metrics_collector
        self.window_size = window_size
        self.threshold_std_dev = threshold_std_dev
        self.metric_history = {}
        self.logger = logging.getLogger("anomaly_detector")

    def _get_metric_values(self, metric_name):
        """Retrieve recent values for a given metric."""
        all_values = self.metrics_collector.get_metrics().get(metric_name, [])
        return [item["value"] for item in all_values[-self.window_size:]]

    def detect_anomaly(self, metric_name):
        """Detect anomalies in a given metric using a simple statistical method."""
        values = self._get_metric_values(metric_name)
        if len(values) < self.window_size:
            self.logger.debug(f"Not enough data for anomaly detection for {metric_name}")
            return False, None

        mean = np.mean(values)
        std_dev = np.std(values)
        latest_value = values[-1]

        if std_dev == 0: # Avoid division by zero if all values are the same
            return False, None

        z_score = (latest_value - mean) / std_dev

        if abs(z_score) > self.threshold_std_dev:
            self.logger.warning(f"Anomaly detected for {metric_name}: latest value {latest_value}, mean {mean:.2f}, std_dev {std_dev:.2f}, z-score {z_score:.2f}")
            return True, {"metric": metric_name, "latest_value": latest_value, "mean": mean, "std_dev": std_dev, "z_score": z_score}
        
        return False, None

    def monitor_all_metrics(self):
        """Monitor all recorded metrics for anomalies."""
        anomalies = []
        for metric_name in self.metrics_collector.get_metrics().keys():
            is_anomaly, details = self.detect_anomaly(metric_name)
            if is_anomaly:
                anomalies.append(details)
        return anomalies

