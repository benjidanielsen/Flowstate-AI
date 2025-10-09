import ast
import radon.complexity as r_complexity
import radon.metrics as r_metrics
import logging

class CodeAnalyzer:
    def __init__(self):
        self.logger = logging.getLogger("code_analyzer")

    def analyze_code(self, code_content):
        """Analyze code for complexity, maintainability, and potential issues."""
        try:
            # AST analysis for structure and potential issues
            tree = ast.parse(code_content)
            function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))

            # Radon for complexity and maintainability
            complexity_results = r_complexity.cc_visit(code_content)
            maintainability_results = r_metrics.mi_visit(code_content, multi=True)

            average_complexity = sum(c.complexity for c in complexity_results) / len(complexity_results) if complexity_results else 0
            maintainability_index = sum(m.mi for m in maintainability_results) / len(maintainability_results) if maintainability_results else 0

            # Simple issue detection (example)
            issues = []
            if average_complexity > 15: # Threshold for high complexity
                issues.append({"type": "complexity", "message": "High average cyclomatic complexity detected."})
            if maintainability_index < 65: # Threshold for low maintainability
                issues.append({"type": "maintainability", "message": "Low maintainability index detected."})

            return {
                "function_count": function_count,
                "class_count": class_count,
                "average_complexity": average_complexity,
                "maintainability_index": maintainability_index,
                "issues": issues
            }
        except Exception as e:
            self.logger.error(f"Error analyzing code: {e}")
            return None

