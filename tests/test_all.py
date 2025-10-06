import unittest
import os
import subprocess

class TestUnitModules(unittest.TestCase):
    def test_module1_functionality(self):
        from flowstate_ai.module1 import function1
        result = function1('test input')
        self.assertEqual(result, 'expected output')

    def test_module2_class_behavior(self):
        from flowstate_ai.module2 import SomeClass
        obj = SomeClass()
        self.assertTrue(obj.method() > 0)

class TestIntegration(unittest.TestCase):
    def test_integration_between_modules(self):
        from flowstate_ai.module1 import function1
        from flowstate_ai.module2 import SomeClass
        obj = SomeClass()
        intermediate = function1('input')
        final_result = obj.process(intermediate)
        self.assertIn('processed', final_result)

class TestEndToEnd(unittest.TestCase):
    def test_cli_end_to_end(self):
        # Assuming there is a CLI entrypoint: flowstate-ai
        result = subprocess.run(['flowstate-ai', '--help'], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Usage', result.stdout)

if __name__ == '__main__':
    unittest.main()
