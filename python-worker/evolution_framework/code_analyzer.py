"""
Code Analyzer

Analyzes code for complexity, maintainability, and potential issues.
"""

import ast
import logging
from typing import Dict, List, Any, Optional
from radon.complexity import cc_visit
from radon.metrics import mi_visit
from radon.raw import analyze


class CodeAnalyzer:
    """Analyzes code quality metrics and identifies improvement opportunities."""
    
    def __init__(self):
        """Initialize the code analyzer."""
        self.logger = logging.getLogger("code_analyzer")
    
    def analyze_code(self, code_content: str, file_path: str = "unknown") -> Optional[Dict[str, Any]]:
        """
        Analyze code for complexity, maintainability, and potential issues.
        
        Args:
            code_content: Source code to analyze
            file_path: Path to the file being analyzed
            
        Returns:
            Dictionary with analysis results, or None if analysis fails
        """
        try:
            # Parse AST for structural analysis
            tree = ast.parse(code_content)
            
            # Count structural elements
            function_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
            class_count = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
            import_count = sum(1 for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom)))
            
            # Analyze complexity using Radon
            complexity_results = cc_visit(code_content)
            average_complexity = 0
            max_complexity = 0
            high_complexity_functions = []
            
            if complexity_results:
                complexities = [c.complexity for c in complexity_results]
                average_complexity = sum(complexities) / len(complexities)
                max_complexity = max(complexities)
                
                # Identify high complexity functions (threshold: 10)
                high_complexity_functions = [
                    {"name": c.name, "complexity": c.complexity, "line": c.lineno}
                    for c in complexity_results if c.complexity > 10
                ]
            
            # Analyze maintainability index
            maintainability_results = mi_visit(code_content, multi=True)
            maintainability_index = 0

            if maintainability_results:
                if isinstance(maintainability_results, (list, tuple)):
                    maintainability_scores = list(maintainability_results)
                else:
                    maintainability_scores = [maintainability_results]

                maintainability_index = sum(maintainability_scores) / len(maintainability_scores)
            
            # Analyze raw metrics
            raw_metrics = analyze(code_content)
            
            # Identify issues
            issues = self._identify_issues(
                average_complexity,
                max_complexity,
                maintainability_index,
                raw_metrics,
                high_complexity_functions
            )
            
            # Calculate overall quality score (0-100)
            quality_score = self._calculate_quality_score(
                average_complexity,
                maintainability_index,
                len(issues)
            )
            
            return {
                "file_path": file_path,
                "structure": {
                    "function_count": function_count,
                    "class_count": class_count,
                    "import_count": import_count,
                    "loc": raw_metrics.loc,
                    "lloc": raw_metrics.lloc,
                    "sloc": raw_metrics.sloc,
                    "comments": raw_metrics.comments,
                    "multi": raw_metrics.multi,
                    "blank": raw_metrics.blank
                },
                "complexity": {
                    "average": round(average_complexity, 2),
                    "max": max_complexity,
                    "high_complexity_functions": high_complexity_functions
                },
                "maintainability": {
                    "index": round(maintainability_index, 2),
                    "rating": self._get_maintainability_rating(maintainability_index)
                },
                "quality_score": round(quality_score, 2),
                "issues": issues
            }
            
        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error analyzing code in {file_path}: {e}")
            return None
    
    def _identify_issues(
        self,
        average_complexity: float,
        max_complexity: float,
        maintainability_index: float,
        raw_metrics: Any,
        high_complexity_functions: List[Dict]
    ) -> List[Dict[str, str]]:
        """
        Identify code quality issues.
        
        Args:
            average_complexity: Average cyclomatic complexity
            max_complexity: Maximum cyclomatic complexity
            maintainability_index: Maintainability index score
            raw_metrics: Raw code metrics
            high_complexity_functions: List of high complexity functions
            
        Returns:
            List of identified issues
        """
        issues = []
        
        # Complexity issues
        if average_complexity > 10:
            issues.append({
                "type": "complexity",
                "severity": "high",
                "message": f"High average cyclomatic complexity: {average_complexity:.2f} (threshold: 10)"
            })
        elif average_complexity > 7:
            issues.append({
                "type": "complexity",
                "severity": "medium",
                "message": f"Moderate average cyclomatic complexity: {average_complexity:.2f} (threshold: 7)"
            })
        
        if max_complexity > 15:
            issues.append({
                "type": "complexity",
                "severity": "high",
                "message": f"Very high maximum complexity: {max_complexity} (threshold: 15)"
            })
        
        # Maintainability issues
        if maintainability_index < 20:
            issues.append({
                "type": "maintainability",
                "severity": "critical",
                "message": f"Very low maintainability index: {maintainability_index:.2f} (threshold: 20)"
            })
        elif maintainability_index < 50:
            issues.append({
                "type": "maintainability",
                "severity": "high",
                "message": f"Low maintainability index: {maintainability_index:.2f} (threshold: 50)"
            })
        elif maintainability_index < 65:
            issues.append({
                "type": "maintainability",
                "severity": "medium",
                "message": f"Moderate maintainability index: {maintainability_index:.2f} (threshold: 65)"
            })
        
        # Code size issues
        if raw_metrics.loc > 500:
            issues.append({
                "type": "size",
                "severity": "medium",
                "message": f"Large file: {raw_metrics.loc} lines of code (threshold: 500)"
            })
        
        # Comment ratio issues
        if raw_metrics.loc > 0:
            comment_ratio = raw_metrics.comments / raw_metrics.loc
            if comment_ratio < 0.1:
                issues.append({
                    "type": "documentation",
                    "severity": "low",
                    "message": f"Low comment ratio: {comment_ratio:.2%} (threshold: 10%)"
                })
        
        # High complexity function details
        if high_complexity_functions:
            issues.append({
                "type": "complexity",
                "severity": "high",
                "message": f"Found {len(high_complexity_functions)} high-complexity functions",
                "details": high_complexity_functions
            })
        
        return issues
    
    def _get_maintainability_rating(self, maintainability_index: float) -> str:
        """
        Get maintainability rating based on index.
        
        Args:
            maintainability_index: Maintainability index score
            
        Returns:
            Rating string
        """
        if maintainability_index >= 85:
            return "A (Excellent)"
        elif maintainability_index >= 65:
            return "B (Good)"
        elif maintainability_index >= 50:
            return "C (Fair)"
        elif maintainability_index >= 20:
            return "D (Poor)"
        else:
            return "F (Critical)"
    
    def _calculate_quality_score(
        self,
        average_complexity: float,
        maintainability_index: float,
        issue_count: int
    ) -> float:
        """
        Calculate overall quality score (0-100).
        
        Args:
            average_complexity: Average cyclomatic complexity
            maintainability_index: Maintainability index score
            issue_count: Number of identified issues
            
        Returns:
            Quality score (0-100)
        """
        # Start with maintainability index (0-100)
        score = maintainability_index
        
        # Penalize for high complexity (up to -30 points)
        complexity_penalty = min(30, max(0, (average_complexity - 5) * 3))
        score -= complexity_penalty
        
        # Penalize for issues (up to -20 points)
        issue_penalty = min(20, issue_count * 2)
        score -= issue_penalty
        
        # Ensure score is within bounds
        return max(0, min(100, score))
    
    def analyze_project(self, project_root: str, extensions: List[str] = None) -> Dict[str, Any]:
        """
        Analyze all code files in a project.
        
        Args:
            project_root: Root directory of the project
            extensions: List of file extensions to analyze (default: ['.py'])
            
        Returns:
            Dictionary with project-wide analysis results
        """
        import os
        
        if extensions is None:
            extensions = ['.py']
        
        self.logger.info(f"Analyzing project: {project_root}")
        
        file_analyses = []
        total_loc = 0
        total_issues = 0
        quality_scores = []
        
        for root, _, files in os.walk(project_root):
            # Skip certain directories
            if any(skip in root for skip in ['node_modules', 'venv', '.git', '__pycache__', 'dist', 'build']):
                continue
            
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                        
                        analysis = self.analyze_code(code_content, file_path)
                        
                        if analysis:
                            file_analyses.append(analysis)
                            total_loc += analysis['structure']['loc']
                            total_issues += len(analysis['issues'])
                            quality_scores.append(analysis['quality_score'])
                    
                    except Exception as e:
                        self.logger.error(f"Error processing {file_path}: {e}")
        
        # Calculate project-wide metrics
        average_quality_score = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        # Identify files needing attention
        files_needing_attention = sorted(
            [a for a in file_analyses if a['quality_score'] < 70],
            key=lambda x: x['quality_score']
        )
        
        return {
            "project_root": project_root,
            "total_files": len(file_analyses),
            "total_loc": total_loc,
            "total_issues": total_issues,
            "average_quality_score": round(average_quality_score, 2),
            "files_needing_attention": files_needing_attention[:10],  # Top 10
            "file_analyses": file_analyses
        }

