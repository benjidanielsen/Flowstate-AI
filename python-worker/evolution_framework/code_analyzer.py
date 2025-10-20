"""Simplified code analyzer for development smoke tests."""
from __future__ import annotations

import ast
import logging
from typing import Any, Dict, List, Optional


class CodeAnalyzer:
    """Analyzes Python source with lightweight heuristics."""

    def __init__(self) -> None:
        self.logger = logging.getLogger("code_analyzer")

    def analyze_code(self, code_content: str, file_path: str = "unknown") -> Optional[Dict[str, Any]]:
        try:
            tree = ast.parse(code_content)
        except SyntaxError as exc:  # pragma: no cover - mirrors previous behaviour
            self.logger.error("Syntax error in %s: %s", file_path, exc)
            return None

        function_count = sum(isinstance(node, ast.FunctionDef) for node in ast.walk(tree))
        class_count = sum(isinstance(node, ast.ClassDef) for node in ast.walk(tree))
        import_count = sum(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(tree))
        lines = code_content.splitlines()
        loc = len(lines)
        comment_lines = sum(1 for line in lines if line.strip().startswith("#"))

        complexity = self._estimate_complexity(tree)
        issues = self._identify_issues(complexity, loc, comment_lines)
        quality_score = self._calculate_quality_score(complexity, len(issues))

        return {
            "file_path": file_path,
            "structure": {
                "function_count": function_count,
                "class_count": class_count,
                "import_count": import_count,
                "loc": loc,
                "lloc": loc,
                "sloc": loc - comment_lines,
                "comments": comment_lines,
                "multi": 0,
                "blank": sum(1 for line in lines if not line.strip()),
            },
            "complexity": {
                "average": complexity,
                "max": complexity,
                "high_complexity_functions": [],
            },
            "maintainability": {
                "index": max(0, 100 - complexity * 5),
                "rating": self._get_maintainability_rating(max(0, 100 - complexity * 5)),
            },
            "quality_score": quality_score,
            "issues": issues,
        }

    # Internal helpers ---------------------------------------------------------
    def _estimate_complexity(self, tree: ast.AST) -> float:
        branch_nodes = (
            ast.If,
            ast.For,
            ast.AsyncFor,
            ast.While,
            ast.Try,
            ast.With,
            ast.BoolOp,
            ast.Match,
        )
        return sum(isinstance(node, branch_nodes) for node in ast.walk(tree)) + 1

    def _identify_issues(self, complexity: float, loc: int, comment_lines: int) -> List[Dict[str, Any]]:
        issues: List[Dict[str, Any]] = []
        if complexity > 15:
            issues.append({"type": "complexity", "severity": "high", "message": "High structural complexity"})
        elif complexity > 8:
            issues.append({"type": "complexity", "severity": "medium", "message": "Moderate structural complexity"})

        if loc > 400:
            issues.append({"type": "size", "severity": "medium", "message": "Large module"})

        if loc and (comment_lines / loc) < 0.1:
            issues.append({"type": "documentation", "severity": "low", "message": "Low comment density"})

        return issues

    def _calculate_quality_score(self, complexity: float, issue_count: int) -> float:
        score = max(0.0, 100.0 - complexity * 3 - issue_count * 5)
        return round(score, 2)

    def _get_maintainability_rating(self, index: float) -> str:
        if index >= 70:
            return "excellent"
        if index >= 50:
            return "good"
        if index >= 30:
            return "fair"
        return "poor"
