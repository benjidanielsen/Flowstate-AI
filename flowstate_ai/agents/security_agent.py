import os
import subprocess
import json
import re
from typing import List, Dict, Optional

class SecurityAgent:
    """
    SecurityAgent performs security audits, vulnerability scanning, and applies fixes.
    It supports scanning Python and JavaScript projects using bandit and npm audit respectively.
    """

    def __init__(self, project_path: str):
        self.project_path = project_path

    def run_bandit_scan(self) -> Dict:
        """Run Bandit security scanner on Python code."""
        try:
            result = subprocess.run(
                ["bandit", "-r", self.project_path, "-f", "json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True,
                text=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            return {"error": "Bandit scan failed", "details": e.stderr}

    def run_npm_audit(self) -> Dict:
        """Run npm audit for JavaScript dependencies."""
        try:
            # npm audit --json outputs JSON formatted audit report
            result = subprocess.run(
                ["npm", "audit", "--json"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_path,
                check=True,
                text=True
            )
            return json.loads(result.stdout)
        except subprocess.CalledProcessError as e:
            # npm audit returns non-zero code if vulnerabilities found, but still outputs JSON
            try:
                return json.loads(e.stdout)
            except Exception:
                return {"error": "npm audit failed", "details": e.stderr}

    def parse_bandit_results(self, bandit_result: Dict) -> List[Dict]:
        """Extract relevant vulnerability info from bandit JSON output."""
        issues = []
        if "results" in bandit_result:
            for issue in bandit_result["results"]:
                issues.append({
                    "filename": issue.get("filename"),
                    "line_number": issue.get("line_number"),
                    "issue_text": issue.get("issue_text"),
                    "severity": issue.get("issue_severity"),
                    "confidence": issue.get("issue_confidence"),
                    "test_id": issue.get("test_id")
                })
        return issues

    def parse_npm_audit_results(self, audit_result: Dict) -> List[Dict]:
        """Extract relevant vulnerability info from npm audit JSON output."""
        vulnerabilities = []
        if "advisories" in audit_result:
            for adv in audit_result["advisories"].values():
                vulnerabilities.append({
                    "module_name": adv.get("module_name"),
                    "severity": adv.get("severity"),
                    "title": adv.get("title"),
                    "vulnerable_versions": adv.get("vulnerable_versions"),
                    "patched_versions": adv.get("patched_versions"),
                    "recommendation": adv.get("recommendation"),
                    "url": adv.get("url")
                })
        elif "vulnerabilities" in audit_result:  # npm v7+ format
            for module_name, info in audit_result["vulnerabilities"].items():
                vulnerabilities.append({
                    "module_name": module_name,
                    "severity": info.get("severity"),
                    "via": info.get("via"),
                    "effects": info.get("effects"),
                    "range": info.get("range"),
                    "fix_available": info.get("fixAvailable")
                })
        return vulnerabilities

    def fix_bandit_issues(self, issues: List[Dict]) -> List[str]:
        """Attempt basic auto-fixes or recommendations for Bandit issues."""
        fixes = []
        for issue in issues:
            test_id = issue.get("test_id")
            filename = issue.get("filename")
            line = issue.get("line_number")
            # Example fix suggestions for common Bandit issues
            if test_id == "B303":  # pickle usage
                fixes.append(f"[FIX RECOMMENDATION] Avoid using pickle in {filename} line {line}, consider safer alternatives like json or cryptography module.")
            elif test_id == "B105":  # hardcoded password
                fixes.append(f"[FIX RECOMMENDATION] Remove hardcoded password in {filename} line {line}, use environment variables or secrets manager.")
            elif test_id == "B101":  # assert statement
                fixes.append(f"[FIX RECOMMENDATION] Avoid assert statements for data validation in {filename} line {line}, use explicit checks and raise exceptions.")
            else:
                fixes.append(f"[INFO] Review issue {test_id} in {filename} line {line}: {issue.get('issue_text')}")
        return fixes

    def fix_npm_vulnerabilities(self, vulnerabilities: List[Dict]) -> List[str]:
        """Attempt automatic fixes for npm audit vulnerabilities."""
        fixes = []
        # Simplest fix: run `npm audit fix`
        try:
            result = subprocess.run(
                ["npm", "audit", "fix"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=self.project_path,
                check=True,
                text=True
            )
            fixes.append("npm audit fix executed successfully.")
        except subprocess.CalledProcessError as e:
            fixes.append(f"npm audit fix failed: {e.stderr}")

        # Additional manual recommendations
        for vuln in vulnerabilities:
            if vuln.get("fix_available") == True:
                fixes.append(f"[INFO] Fix available for module {vuln.get('module_name')}, try updating dependency.")
            elif vuln.get("severity") in ["high", "critical"]:
                fixes.append(f"[WARNING] High severity vulnerability in {vuln.get('module_name')}, consider manual remediation.")

        return fixes

    def run_security_audit(self) -> Dict:
        """Perform security audit for both Python and JavaScript code."""
        report = {}

        # Python audit with Bandit
        bandit_result = self.run_bandit_scan()
        if "error" not in bandit_result:
            python_issues = self.parse_bandit_results(bandit_result)
            report["python_issues"] = python_issues
            report["python_fixes"] = self.fix_bandit_issues(python_issues)
        else:
            report["python_error"] = bandit_result.get("error")

        # JavaScript audit with npm audit
        npm_result = self.run_npm_audit()
        if "error" not in npm_result:
            npm_vulnerabilities = self.parse_npm_audit_results(npm_result)
            report["npm_vulnerabilities"] = npm_vulnerabilities
            report["npm_fixes"] = self.fix_npm_vulnerabilities(npm_vulnerabilities)
        else:
            report["npm_error"] = npm_result.get("error")

        return report


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Run security audits on a project.")
    parser.add_argument("project_path", help="Path to the project directory to scan.")
    args = parser.parse_args()

    agent = SecurityAgent(args.project_path)
    audit_report = agent.run_security_audit()
    print(json.dumps(audit_report, indent=2))
