#!/usr/bin/env python3
"""
🧠 PROACTIVE PROBLEM SOLVER AI 🧠
Scans project files to identify potential future problems and proposes solutions.
"""

import os
import json
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Configuration
PROJECT_ROOT = Path("/home/ubuntu/Flowstate-AI")
REPORT_DIR = PROJECT_ROOT / "innovation-reports" / "problem-identification"

# Keywords and patterns for problem identification
PROBLEM_PATTERNS = {
    "hardcoded_credentials": {
        "pattern": r"(api_key|secret|token|password)\s*=\s*['\"](?!\s*os\.getenv)[^'\"]+['\"]",
        "description": "Hardcoded credentials are a security risk.",
        "severity": "CRITICAL"
    },
    "outdated_dependencies": {
        "pattern": r"(package\.json|requirements\.txt|setup\.py)", # This will require deeper analysis
        "description": "Outdated dependencies can lead to security vulnerabilities and compatibility issues.",
        "severity": "HIGH"
    },
    "unhandled_exceptions": {
        "pattern": r"try:\s*\n(?!\s*except)",
        "description": "Missing exception handling can cause unexpected crashes.",
        "severity": "MEDIUM"
    },
    "large_untested_files": {
        "pattern": r"\.py|\.js|\.ts", # Identify large files, then check for tests
        "description": "Large, untested files are prone to bugs and difficult to maintain.",
        "severity": "HIGH"
    },
    "inefficient_database_queries": {
        "pattern": r"(SELECT\s+\*|FROM\s+.*?\s+WHERE\s+.*?\s+LIKE)", # Basic pattern, needs more context
        "description": "Inefficient database queries can lead to performance bottlenecks.",
        "severity": "MEDIUM"
    },
    "missing_documentation": {
        "pattern": r"(def\s+\w+\(|class\s+\w+:\s*\n(?!\s*\"\"\"))", # Functions/classes without docstrings
        "description": "Missing documentation makes code harder to understand and maintain.",
        "severity": "LOW"
    },
    "todo_comments": {
        "pattern": r"#\s*TODO|//\s*TODO",
        "description": "TODO comments indicate unfinished work or potential future issues.",
        "severity": "LOW"
    }
}

# File types to scan
SCAN_FILE_TYPES = [".py", ".js", ".ts", ".md", ".json", ".txt", ".sh", ".bat"]

def get_all_project_files(root_dir: Path) -> List[Path]:
    """Recursively get all relevant project files."""
    file_list = []
    for path in root_dir.rglob("*"):
        if path.is_file() and path.suffix in SCAN_FILE_TYPES:
            # Exclude common ignored directories
            if not any(part.startswith(".") or part in ["node_modules", "__pycache__", "venv", "env"] for part in path.parts):
                file_list.append(path)
    return file_list

def analyze_file_for_problems(file_path: Path) -> List[Dict[str, Any]]:
    """Analyze a single file for predefined problem patterns."""
    problems = []
    try:
        content = file_path.read_text()
        lines = content.splitlines()
        for i, line in enumerate(lines):
            for problem_type, details in PROBLEM_PATTERNS.items():
                if re.search(details["pattern"], line, re.IGNORECASE):
                    # Special handling for 'outdated_dependencies' - requires more context
                    if problem_type == "outdated_dependencies":
                        # This is a placeholder. Real implementation would involve
                        # parsing package.json/requirements.txt and checking against latest versions.
                        # For now, just flag the file.
                        if file_path.name in ["package.json", "requirements.txt", "setup.py"]:
                            problems.append({
                                "type": problem_type,
                                "description": details["description"],
                                "severity": details["severity"],
                                "file": str(file_path.relative_to(PROJECT_ROOT)),
                                "line": i + 1,
                                "context": line.strip()
                            })
                    elif problem_type == "large_untested_files":
                        # Placeholder: actual check would involve file size and test file existence
                        # For now, just flag files that match the pattern
                        if file_path.suffix in [".py", ".js", ".ts"] and len(lines) > 500: # Example: >500 lines is large
                             # Further check for test files (e.g., test_*.py, *.test.js)
                             test_file_exists = False
                             test_patterns = [f"test_{file_path.stem}.py", f"{file_path.stem}.test.js", f"{file_path.stem}.test.ts"]
                             for tp in test_patterns:
                                 if (file_path.parent / tp).exists():
                                     test_file_exists = True
                                     break
                             if not test_file_exists:
                                 problems.append({
                                     "type": problem_type,
                                     "description": details["description"],
                                     "severity": details["severity"],
                                     "file": str(file_path.relative_to(PROJECT_ROOT)),
                                     "line": "N/A",
                                     "context": f"File size: {len(lines)} lines, no obvious test file found."
                                 })
                    else:
                        problems.append({
                            "type": problem_type,
                            "description": details["description"],
                            "severity": details["severity"],
                            "file": str(file_path.relative_to(PROJECT_ROOT)),
                            "line": i + 1,
                            "context": line.strip()
                        })
    except Exception as e:
        print(f"Error reading or analyzing file {file_path}: {e}")
    return problems

def generate_solution_proposal(problem: Dict[str, Any]) -> str:
    """Generate a solution proposal for a given problem."""
    problem_desc = "**Problem**: {} (Severity: {})".format(problem["description"], problem["severity"])
    problem_location = "**Location**: {}:L{}".format(problem["file"], problem["line"])
    problem_context = "**Context**: `{}`".format(problem["context"])
    solution = problem_desc + "\n" + problem_location + "\n" + problem_context + "\n\n"
    
    if problem["type"] == "hardcoded_credentials":
        solution += """**Proposed Solution**: Replace hardcoded credentials with environment variables or a secure configuration management system. Update the code to retrieve the value using `os.getenv()` or similar secure methods. Ensure the `.env` file is not committed to version control.\n"""
    elif problem["type"] == "outdated_dependencies":
        solution += """**Proposed Solution**: Review 'package.json' or 'requirements.txt' for outdated dependencies. Use 'npm outdated' (for Node.js) or 'pip list --outdated' (for Python) to identify and update dependencies to their latest stable versions. Implement a dependency scanning tool for continuous monitoring.\n"""
    elif problem["type"] == "unhandled_exceptions":
        solution += """**Proposed Solution**: Implement robust `try-except` blocks to gracefully handle potential exceptions. Log errors for debugging and provide user-friendly feedback where appropriate. Consider using a centralized error logging system.\n"""
    elif problem["type"] == "large_untested_files":
        solution += """**Proposed Solution**: Break down the large file into smaller, more manageable modules or functions. Write comprehensive unit and integration tests for all critical components. Implement code coverage tools to ensure adequate test coverage.\n"""
    elif problem["type"] == "inefficient_database_queries":
        solution += """**Proposed Solution**: Analyze the database query for performance bottlenecks. Consider adding appropriate database indexes, optimizing `WHERE` clauses, or refactoring the query to retrieve only necessary data. Use an ORM or query builder to construct efficient queries.\n"""
    elif problem["type"] == "missing_documentation":
        solution += """**Proposed Solution**: Add clear and concise docstrings to functions, classes and modules. Ensure that the documentation explains the purpose, arguments, return values, and any side effects of the code. Maintain a `README.md` file for overall project documentation.\n"""
    elif problem["type"] == "todo_comments":
        solution += """**Proposed Solution**: Review and address all `TODO` comments. Either implement the suggested changes, create a new task for them, or remove the comment if it's no longer relevant. Regularly clean up technical debt indicated by `TODO`s.\n"""
    else:
        solution += """**Proposed Solution**: Further investigation is required to determine the best course of action for this problem.\n"""
        
    return solution

def main():
    print("🧠 Starting Proactive Problem Solver AI...")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    
    all_problems = []
    project_files = get_all_project_files(PROJECT_ROOT)
    
    print(f"Scanning {len(project_files)} files for potential problems...")
    for file_path in project_files:
        problems_in_file = analyze_file_for_problems(file_path)
        if problems_in_file:
            all_problems.extend(problems_in_file)
            
    if not all_problems:
        print("✅ No significant potential problems identified at this time.")
        report_content = "# Proactive Problem Identification Report\n\nNo significant potential problems identified at this time. The project appears to be in good health.\n"
    else:
        print(f"⚠️  Identified {len(all_problems)} potential problems.")
        report_content = "# Proactive Problem Identification Report\n\nThis report identifies potential future problems and areas for optimization within the FlowState-AI project, based on an autonomous scan of the codebase.\n\n## Summary of Findings\n\n| Severity | Type | File | Line | Description | Proposed Solution |\n|---|---|---|---|---|---|\n"
        
        # Sort problems by severity (CRITICAL, HIGH, MEDIUM, LOW)
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        all_problems.sort(key=lambda p: severity_order.get(p["severity"], 0), reverse=True)
        
        for problem in all_problems:
            solution_proposal = generate_solution_proposal(problem)
            report_content += "| {} | {} | {} | {} | {} | {} |\n".format(
                problem["severity"],
                problem["type"].replace("_", " ").title(),
                problem["file"],
                problem["line"],
                problem["description"],
                solution_proposal.replace("\n", "<br>")
            )


    report_filename = "problem_report_{}.md".format(datetime.now().strftime("%Y%m%d_%H%M%S"))
    report_path = REPORT_DIR / report_filename
    report_path.write_text(report_content)
    print(f"✅ Problem identification report generated: {report_path}")

if __name__ == "__main__":
    main()
