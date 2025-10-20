import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from evolution_framework.metrics_collector import MetricsCollector
from evolution_framework.knowledge_manager import VectorKnowledgeManager
from evolution_framework.code_analyzer import CodeAnalyzer
from evolution_framework.anomaly_detector import AnomalyDetector
from evolution_framework.evolution_governor import EvolutionGovernor

class TestEvolutionFramework(unittest.TestCase):
    
    def test_metrics_collector(self):
        """Test metrics collection"""
        collector = MetricsCollector("test")
        collector.record_metric("test_metric", 100)
        metrics = collector.get_metrics()
        self.assertIn("test_metric", metrics)
        self.assertEqual(metrics["test_metric"][-1]["value"], 100)
    
    def test_code_analyzer(self):
        """Test code analysis"""
        analyzer = CodeAnalyzer()
        test_code = """
def simple_function():
    return 42
"""
        result = analyzer.analyze_code(test_code)
        self.assertIsNotNone(result)
        self.assertIn("complexity", result)
        self.assertIn("maintainability", result)
    
    def test_anomaly_detector(self):
        """Test anomaly detection"""
        collector = MetricsCollector("test")
        # Add normal values
        for i in range(10):
            collector.record_metric("test_metric", 100)
        
        detector = AnomalyDetector(collector)
        is_anomaly, _ = detector.detect_anomaly("test_metric")
        self.assertFalse(is_anomaly)
        
        # Add anomalous value
        collector.record_metric("test_metric", 1000)
        is_anomaly, details = detector.detect_anomaly("test_metric")
        self.assertTrue(is_anomaly)
    
    def test_evolution_governor(self):
        """Test evolution governance"""
        collector = MetricsCollector("test")
        detector = AnomalyDetector(collector)
        governor = EvolutionGovernor(detector, collector)
        
        # Test safe mode activation
        governor.activate_safe_mode("test_reason")
        self.assertTrue(governor.safe_mode_active)
        
        # Test safe mode deactivation
        governor.deactivate_safe_mode()
        self.assertFalse(governor.safe_mode_active)

if __name__ == '__main__':
    unittest.main()
