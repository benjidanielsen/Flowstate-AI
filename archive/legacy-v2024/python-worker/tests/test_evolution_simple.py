import unittest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestEvolutionFrameworkSimple(unittest.TestCase):
    
    def test_code_analyzer_import(self):
        """Test that CodeAnalyzer can be imported"""
        try:
            from evolution_framework.code_analyzer import CodeAnalyzer
            analyzer = CodeAnalyzer()
            self.assertIsNotNone(analyzer)
        except Exception as e:
            self.fail(f"Failed to import CodeAnalyzer: {e}")
    
    def test_anomaly_detector_import(self):
        """Test that AnomalyDetector can be imported"""
        try:
            from evolution_framework.anomaly_detector import AnomalyDetector
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import AnomalyDetector: {e}")
    
    def test_evolution_governor_import(self):
        """Test that EvolutionGovernor can be imported"""
        try:
            from evolution_framework.evolution_governor import EvolutionGovernor
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import EvolutionGovernor: {e}")
    
    def test_evolution_manager_import(self):
        """Test that EvolutionManager can be imported"""
        try:
            from evolution_framework.evolution_manager import EvolutionManager
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import EvolutionManager: {e}")
    
    def test_knowledge_manager_import(self):
        """Test that VectorKnowledgeManager can be imported"""
        try:
            from evolution_framework.knowledge_manager import VectorKnowledgeManager
            self.assertTrue(True)
        except Exception as e:
            self.fail(f"Failed to import VectorKnowledgeManager: {e}")

if __name__ == '__main__':
    unittest.main()

