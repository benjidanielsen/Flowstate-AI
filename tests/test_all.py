import unittest
import os
import sys
import json
import datetime

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class TestTaskGenerator(unittest.TestCase):
    """Test the TaskGenerator module"""
    
    def test_task_generator_initialization(self):
        """Test TaskGenerator can be initialized"""
        from flowstate_ai.task_generator import TaskGenerator
        generator = TaskGenerator()
        self.assertEqual(generator.project_name, "Flowstate-AI")
    
    def test_task_generator_custom_project(self):
        """Test TaskGenerator with custom project name"""
        from flowstate_ai.task_generator import TaskGenerator
        generator = TaskGenerator(project_name="Test Project")
        self.assertEqual(generator.project_name, "Test Project")
    
    def test_generate_next_week_tasks(self):
        """Test task generation returns correct structure"""
        from flowstate_ai.task_generator import TaskGenerator
        generator = TaskGenerator()
        result = generator.generate_next_week_tasks()
        
        self.assertIn('project', result)
        self.assertIn('week_start', result)
        self.assertIn('week_end', result)
        self.assertIn('tasks', result)
        self.assertIsInstance(result['tasks'], list)
        self.assertTrue(len(result['tasks']) > 0)

class TestDataExporter(unittest.TestCase):
    """Test the DataExporter module"""
    
    def setUp(self):
        """Set up test data"""
        self.test_data = [
            {"name": "Alice", "age": 30, "city": "New York"},
            {"name": "Bob", "age": 25, "city": "Los Angeles"}
        ]
    
    def test_exporter_initialization(self):
        """Test DataExporter can be initialized"""
        from flowstate_ai.exporter import DataExporter
        exporter = DataExporter(self.test_data)
        self.assertEqual(exporter.data, self.test_data)
    
    def test_to_json_export(self):
        """Test JSON export functionality"""
        from flowstate_ai.exporter import DataExporter
        exporter = DataExporter(self.test_data)
        json_output = exporter.to_json()
        
        self.assertIsInstance(json_output, str)
        parsed = json.loads(json_output)
        self.assertEqual(len(parsed), 2)
        self.assertEqual(parsed[0]['name'], 'Alice')
    
    def test_to_csv_export(self):
        """Test CSV export functionality"""
        from flowstate_ai.exporter import DataExporter
        exporter = DataExporter(self.test_data)
        csv_output = exporter.to_csv()
        
        self.assertIsInstance(csv_output, str)
        self.assertIn('name,age,city', csv_output)
        self.assertIn('Alice', csv_output)
    
    def test_empty_data_export(self):
        """Test exporting empty data"""
        from flowstate_ai.exporter import DataExporter
        exporter = DataExporter([])
        csv_output = exporter.to_csv()
        json_output = exporter.to_json()
        
        self.assertEqual(csv_output, "")
        self.assertEqual(json_output, "[]")

class TestIntegration(unittest.TestCase):
    """Test integration between modules"""
    
    def test_task_generator_with_exporter(self):
        """Test that TaskGenerator output can be exported"""
        from flowstate_ai.task_generator import TaskGenerator
        from flowstate_ai.exporter import DataExporter
        
        generator = TaskGenerator()
        result = generator.generate_next_week_tasks()
        
        # Export tasks as JSON
        exporter = DataExporter(result['tasks'])
        json_output = exporter.to_json()
        
        self.assertIsInstance(json_output, str)
        parsed = json.loads(json_output)
        self.assertTrue(len(parsed) > 0)
        self.assertIn('title', parsed[0])

if __name__ == '__main__':
    unittest.main()
