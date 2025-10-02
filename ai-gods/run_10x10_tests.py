#!/usr/bin/env python3
"""
🧪 GODMODE 10x10 TEST RUNNER
⚡ Executes 10 iterations of 10 test runs each (100 total)
🎯 Mission: Identify errors, performance bottlenecks, and improvement opportunities
🚀 Features: Comprehensive tracking, analysis, and reporting
"""

import json
import logging
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

# Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
ITERATIONS = 10
RUNS_PER_ITERATION = 10
TOTAL_RUNS = ITERATIONS * RUNS_PER_ITERATION

# Setup logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='🧪 [10x10] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/10x10-test-runner.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TestRunner:
    """Manages 10x10 test execution and analysis"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.test_script = self.project_root / "ai-gods" / "test_suite_comprehensive.py"
        self.results = []
        self.errors_found = []
        self.improvements_identified = []
    
    def run_single_test(self, iteration: int, run: int) -> Dict[str, Any]:
        """Run a single test execution"""
        logger.info(f"🔄 Running Iteration {iteration}, Run {run}...")
        
        start_time = time.time()
        
        try:
            result = subprocess.run(
                [sys.executable, str(self.test_script)],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=60
            )
            
            elapsed_time = time.time() - start_time
            
            # Parse output
            output = result.stdout + result.stderr
            tests_run = 0
            successes = 0
            failures = 0
            errors = 0
            
            for line in output.split('\n'):
                if "Tests run:" in line:
                    tests_run = int(line.split("Tests run:")[1].split()[0])
                elif "Successes:" in line:
                    successes = int(line.split("Successes:")[1].split()[0])
                elif "Failures:" in line:
                    failures = int(line.split("Failures:")[1].split()[0])
                elif "Errors:" in line:
                    errors = int(line.split("Errors:")[1].split()[0])
            
            test_result = {
                "iteration": iteration,
                "run": run,
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": elapsed_time,
                "tests_run": tests_run,
                "successes": successes,
                "failures": failures,
                "errors": errors,
                "return_code": result.returncode,
                "output": output
            }
            
            if failures > 0 or errors > 0:
                logger.warning(f"⚠️  Iteration {iteration}, Run {run}: {failures} failures, {errors} errors")
                self.errors_found.append(test_result)
            else:
                logger.info(f"✅ Iteration {iteration}, Run {run}: All tests passed in {elapsed_time:.3f}s")
            
            return test_result
            
        except subprocess.TimeoutExpired:
            logger.error(f"❌ Iteration {iteration}, Run {run}: Test execution timed out")
            return {
                "iteration": iteration,
                "run": run,
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": 60.0,
                "tests_run": 0,
                "successes": 0,
                "failures": 0,
                "errors": 1,
                "return_code": -1,
                "output": "Test execution timed out"
            }
        except Exception as e:
            logger.error(f"❌ Iteration {iteration}, Run {run}: Exception - {str(e)}")
            return {
                "iteration": iteration,
                "run": run,
                "timestamp": datetime.now().isoformat(),
                "elapsed_time": 0.0,
                "tests_run": 0,
                "successes": 0,
                "failures": 0,
                "errors": 1,
                "return_code": -1,
                "output": str(e)
            }
    
    def run_all_tests(self):
        """Run all 10x10 test iterations"""
        logger.info("🚀 STARTING 10x10 TEST EXECUTION")
        logger.info("=" * 80)
        logger.info(f"Total iterations: {ITERATIONS}")
        logger.info(f"Runs per iteration: {RUNS_PER_ITERATION}")
        logger.info(f"Total test runs: {TOTAL_RUNS}")
        logger.info("=" * 80)
        
        overall_start_time = time.time()
        
        for iteration in range(1, ITERATIONS + 1):
            logger.info(f"\n📊 ITERATION {iteration}/{ITERATIONS}")
            logger.info("-" * 80)
            
            iteration_start_time = time.time()
            
            for run in range(1, RUNS_PER_ITERATION + 1):
                result = self.run_single_test(iteration, run)
                self.results.append(result)
                
                # Small delay between runs
                time.sleep(0.1)
            
            iteration_elapsed = time.time() - iteration_start_time
            logger.info(f"⏱️  Iteration {iteration} completed in {iteration_elapsed:.2f}s")
        
        overall_elapsed = time.time() - overall_start_time
        logger.info("\n" + "=" * 80)
        logger.info(f"✅ ALL 10x10 TESTS COMPLETED in {overall_elapsed:.2f}s")
        logger.info("=" * 80)
    
    def analyze_results(self):
        """Analyze test results and identify patterns"""
        logger.info("\n🔍 ANALYZING TEST RESULTS...")
        logger.info("=" * 80)
        
        total_tests = len(self.results)
        successful_runs = sum(1 for r in self.results if r["failures"] == 0 and r["errors"] == 0)
        failed_runs = total_tests - successful_runs
        
        total_elapsed_time = sum(r["elapsed_time"] for r in self.results)
        avg_elapsed_time = total_elapsed_time / total_tests if total_tests > 0 else 0
        min_elapsed_time = min(r["elapsed_time"] for r in self.results) if self.results else 0
        max_elapsed_time = max(r["elapsed_time"] for r in self.results) if self.results else 0
        
        logger.info(f"Total test runs: {total_tests}")
        logger.info(f"Successful runs: {successful_runs} ({successful_runs/total_tests*100:.1f}%)")
        logger.info(f"Failed runs: {failed_runs} ({failed_runs/total_tests*100:.1f}%)")
        logger.info(f"Average execution time: {avg_elapsed_time:.3f}s")
        logger.info(f"Min execution time: {min_elapsed_time:.3f}s")
        logger.info(f"Max execution time: {max_elapsed_time:.3f}s")
        
        # Identify performance issues
        if max_elapsed_time > avg_elapsed_time * 1.5:
            self.improvements_identified.append({
                "type": "PERFORMANCE",
                "severity": "MEDIUM",
                "description": f"Execution time variance detected: max {max_elapsed_time:.3f}s vs avg {avg_elapsed_time:.3f}s",
                "recommendation": "Investigate slow test runs and optimize performance"
            })
        
        # Identify error patterns
        if failed_runs > 0:
            error_types = {}
            for error in self.errors_found:
                key = f"failures:{error['failures']},errors:{error['errors']}"
                error_types[key] = error_types.get(key, 0) + 1
            
            logger.info("\n📊 ERROR PATTERNS:")
            for error_type, count in error_types.items():
                logger.info(f"  - {error_type}: {count} occurrences")
                self.improvements_identified.append({
                    "type": "ERROR",
                    "severity": "HIGH",
                    "description": f"Error pattern detected: {error_type}",
                    "occurrences": count,
                    "recommendation": "Fix identified errors to improve system reliability"
                })
        
        logger.info("=" * 80)
    
    def generate_report(self):
        """Generate comprehensive test report"""
        logger.info("\n📝 GENERATING COMPREHENSIVE REPORT...")
        
        report = {
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_iterations": ITERATIONS,
                "runs_per_iteration": RUNS_PER_ITERATION,
                "total_runs": TOTAL_RUNS
            },
            "summary": {
                "total_tests": len(self.results),
                "successful_runs": sum(1 for r in self.results if r["failures"] == 0 and r["errors"] == 0),
                "failed_runs": sum(1 for r in self.results if r["failures"] > 0 or r["errors"] > 0),
                "total_elapsed_time": sum(r["elapsed_time"] for r in self.results),
                "avg_elapsed_time": sum(r["elapsed_time"] for r in self.results) / len(self.results) if self.results else 0,
                "min_elapsed_time": min(r["elapsed_time"] for r in self.results) if self.results else 0,
                "max_elapsed_time": max(r["elapsed_time"] for r in self.results) if self.results else 0
            },
            "errors_found": self.errors_found,
            "improvements_identified": self.improvements_identified,
            "detailed_results": self.results
        }
        
        # Save report to file
        report_path = Path("godmode-logs/10x10-test-report.json")
        with open(report_path, 'w') as f:
            json.dump(report, indent=2, fp=f)
        
        logger.info(f"✅ Report saved to: {report_path}")
        
        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("📊 10x10 TEST SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total test runs: {report['summary']['total_tests']}")
        logger.info(f"Successful runs: {report['summary']['successful_runs']} ({report['summary']['successful_runs']/report['summary']['total_tests']*100:.1f}%)")
        logger.info(f"Failed runs: {report['summary']['failed_runs']} ({report['summary']['failed_runs']/report['summary']['total_tests']*100:.1f}%)")
        logger.info(f"Average execution time: {report['summary']['avg_elapsed_time']:.3f}s")
        logger.info(f"Total errors found: {len(self.errors_found)}")
        logger.info(f"Improvements identified: {len(self.improvements_identified)}")
        logger.info("=" * 80)
        
        if self.improvements_identified:
            logger.info("\n🔧 RECOMMENDED IMPROVEMENTS:")
            for i, improvement in enumerate(self.improvements_identified, 1):
                logger.info(f"\n{i}. [{improvement['severity']}] {improvement['type']}")
                logger.info(f"   Description: {improvement['description']}")
                logger.info(f"   Recommendation: {improvement['recommendation']}")
        
        logger.info("\n" + "=" * 80)
        
        if report['summary']['failed_runs'] == 0:
            logger.info("✅ ALL 10x10 TESTS PASSED - SYSTEM IS ROBUST AND RELIABLE")
        else:
            logger.info("⚠️  SOME TESTS FAILED - IMPROVEMENTS NEEDED")
        
        logger.info("=" * 80)
        
        return report


def main():
    """Main entry point"""
    # Ensure log directory exists
    log_dir = Path('godmode-logs')
    log_dir.mkdir(exist_ok=True)
    
    # Create and run test runner
    runner = TestRunner()
    runner.run_all_tests()
    runner.analyze_results()
    report = runner.generate_report()
    
    # Return exit code based on results
    if report['summary']['failed_runs'] > 0:
        return 1
    return 0


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)
