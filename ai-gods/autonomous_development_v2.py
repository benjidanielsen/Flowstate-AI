#!/usr/bin/env python3
"""
🚀 AUTONOMOUS DEVELOPMENT SYSTEM v2.0 - Fully Refactored
⚡ GODMODE: Self-healing, self-improving, and self-expanding capabilities
🎯 Mission: Enable truly autonomous software development with maximum efficiency
🧠 Features: Advanced error detection, intelligent fixing, continuous optimization
"""

import asyncio
import sys
import ast
import json
import logging
import platform
import os
import re
import subprocess
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set

# Configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')

# Setup logging

# Ensure UTF-8 encoding for stdout on Windows to support emoji logging
if platform.system() == 'Windows':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.detach())

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='🚀 [AUTO-DEV-v2] %(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('godmode-logs/autonomous-development-v2.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ErrorSeverity(Enum):
    """Error severity levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


class ErrorSource(Enum):
    """Error source types"""
    LOG = "log"
    TEST = "test"
    SYNTAX = "syntax"
    RUNTIME = "runtime"
    DEPENDENCY = "dependency"
    QUALITY = "quality"


@dataclass
class Error:
    """Error data structure"""
    id: str
    source: ErrorSource
    severity: ErrorSeverity
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    component: Optional[str] = None
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ErrorAnalysis:
    """Error analysis result"""
    error: Error
    root_cause: Optional[str] = None
    suggested_fix: Optional[str] = None
    fix_command: Optional[str] = None
    confidence: float = 0.0
    requires_manual_intervention: bool = False


@dataclass
class Fix:
    """Fix data structure"""
    id: str
    error_id: str
    command: str
    timestamp: datetime = field(default_factory=datetime.now)
    success: bool = False
    validated: bool = False
    error_message: Optional[str] = None


class AutonomousDevelopmentV2:
    """
    Autonomous Development System v2.0 - Fully refactored with async operations
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
        # Error and fix tracking
        self.detected_errors: Dict[str, Error] = {}
        self.error_analyses: Dict[str, ErrorAnalysis] = {}
        self.applied_fixes: Dict[str, Fix] = {}
        
        # Pattern matching for common errors
        self.error_patterns = self._init_error_patterns()
        
        # Running state
        self.running = False
        self.auto_heal_task: Optional[asyncio.Task] = None
        self.continuous_improvement_task: Optional[asyncio.Task] = None
        
        logger.info("🚀 AUTONOMOUS DEVELOPMENT v2.0 INITIALIZED")
    
    def _init_error_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize error pattern matching rules"""
        return {
            'missing_dependency': {
                'patterns': [
                    r"module not found",
                    r"cannot find module",
                    r"no module named",
                    r"modulenotfounderror"
                ],
                'root_cause': 'missing_dependency',
                'suggested_fix': 'install_dependency',
                'confidence': 0.9
            },
            'syntax_error': {
                'patterns': [
                    r"syntax error",
                    r"syntaxerror",
                    r"unexpected token"
                ],
                'root_cause': 'syntax_error',
                'suggested_fix': 'fix_syntax',
                'confidence': 0.8
            },
            'service_not_running': {
                'patterns': [
                    r"connection refused",
                    r"econnrefused",
                    r"cannot connect to",
                    r"service unavailable"
                ],
                'root_cause': 'service_not_running',
                'suggested_fix': 'start_service',
                'confidence': 0.85
            },
            'permission_denied': {
                'patterns': [
                    r"permission denied",
                    r"eacces",
                    r"access denied"
                ],
                'root_cause': 'permission_issue',
                'suggested_fix': 'fix_permissions',
                'confidence': 0.9
            },
            'port_in_use': {
                'patterns': [
                    r"address already in use",
                    r"eaddrinuse",
                    r"port.*already.*use"
                ],
                'root_cause': 'port_conflict',
                'suggested_fix': 'kill_process_on_port',
                'confidence': 0.85
            },
            'database_error': {
                'patterns': [
                    r"database.*error",
                    r"connection.*database.*failed",
                    r"sql.*error"
                ],
                'root_cause': 'database_issue',
                'suggested_fix': 'fix_database',
                'confidence': 0.75
            }
        }
    
    async def detect_errors(self) -> List[Error]:
        """Detect errors from various sources"""
        errors = []
        
        # Run detection tasks in parallel
        detection_tasks = [
            self._scan_log_files(),
            self._check_syntax_errors(),
            self._check_dependencies(),
            self._run_tests()
        ]
        
        results = await asyncio.gather(*detection_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, list):
                errors.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"❌ Error detection failed: {result}")
        
        # Store detected errors
        for error in errors:
            self.detected_errors[error.id] = error
        
        logger.info(f"🔍 Detected {len(errors)} errors")
        return errors
    
    async def _scan_log_files(self) -> List[Error]:
        """Scan log files for errors"""
        errors = []
        log_dir = self.project_root / 'godmode-logs'
        
        if not log_dir.exists():
            return errors
        
        for log_file in log_dir.glob('*.log'):
            try:
                with open(log_file, 'r') as f:
                    lines = f.readlines()
                    
                    # Only check recent lines (last 100)
                    recent_lines = lines[-100:] if len(lines) > 100 else lines
                    
                    for i, line in enumerate(recent_lines):
                        if 'ERROR' in line or 'CRITICAL' in line:
                            error_id = f"log_{log_file.name}_{i}_{int(datetime.now().timestamp())}"
                            errors.append(Error(
                                id=error_id,
                                source=ErrorSource.LOG,
                                severity=ErrorSeverity.CRITICAL if 'CRITICAL' in line else ErrorSeverity.HIGH,
                                message=line.strip(),
                                file=str(log_file),
                                line=len(lines) - len(recent_lines) + i + 1
                            ))
            except Exception as e:
                logger.error(f"❌ Error reading log file {log_file}: {e}")
        
        return errors
    
    async def _check_syntax_errors(self) -> List[Error]:
        """Check for syntax errors in Python files"""
        errors = []
        
        for py_file in self.project_root.rglob('*.py'):
            if self._should_skip_file(py_file):
                continue
            
            try:
                with open(py_file, 'r') as f:
                    code = f.read()
                    ast.parse(code)
            except SyntaxError as e:
                error_id = f"syntax_{py_file.name}_{e.lineno}_{int(datetime.now().timestamp())}"
                errors.append(Error(
                    id=error_id,
                    source=ErrorSource.SYNTAX,
                    severity=ErrorSeverity.CRITICAL,
                    message=str(e),
                    file=str(py_file),
                    line=e.lineno
                ))
            except Exception as e:
                logger.error(f"❌ Error checking {py_file}: {e}")
        
        return errors
    
    async def _check_dependencies(self) -> List[Error]:
        """Check for missing dependencies"""
        errors = []
        
        # Check Python dependencies
        requirements_file = self.project_root / 'python-worker' / 'requirements.txt'
        if requirements_file.exists():
            try:
                result = await asyncio.create_subprocess_exec(
                    'pip3', 'check',
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    error_id = f"dep_python_{int(datetime.now().timestamp())}"
                    errors.append(Error(
                        id=error_id,
                        source=ErrorSource.DEPENDENCY,
                        severity=ErrorSeverity.HIGH,
                        message=stderr.decode() if stderr else "Python dependency issues detected",
                        component='python'
                    ))
            except Exception as e:
                logger.error(f"❌ Error checking Python dependencies: {e}")
        
        # Check Node.js dependencies
        for package_json in self.project_root.rglob('package.json'):
            if self._should_skip_file(package_json):
                continue
            
            try:
                result = await asyncio.create_subprocess_exec(
                    'npm', 'ls',
                    cwd=package_json.parent,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                
                if result.returncode != 0:
                    error_id = f"dep_npm_{package_json.parent.name}_{int(datetime.now().timestamp())}"
                    errors.append(Error(
                        id=error_id,
                        source=ErrorSource.DEPENDENCY,
                        severity=ErrorSeverity.MEDIUM,
                        message=stderr.decode() if stderr else "NPM dependency issues detected",
                        component=str(package_json.parent)
                    ))
            except Exception as e:
                logger.error(f"❌ Error checking NPM dependencies: {e}")
        
        return errors
    
    async def _run_tests(self) -> List[Error]:
        """Run automated tests and capture failures"""
        errors = []
        
        # Run Python tests
        if (self.project_root / 'tests').exists():
            try:
                result = await asyncio.create_subprocess_exec(
                    'python3', '-m', 'pytest', '--tb=short',
                    cwd=self.project_root,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await asyncio.wait_for(result.communicate(), timeout=300)
                
                if result.returncode != 0:
                    error_id = f"test_python_{int(datetime.now().timestamp())}"
                    errors.append(Error(
                        id=error_id,
                        source=ErrorSource.TEST,
                        severity=ErrorSeverity.HIGH,
                        message=stderr.decode() if stderr else "Python tests failed",
                        component='tests'
                    ))
            except asyncio.TimeoutError:
                logger.warning("⚠️ Python tests timed out")
            except Exception as e:
                logger.error(f"❌ Error running Python tests: {e}")
        
        return errors
    
    def _should_skip_file(self, file_path: Path) -> bool:
        """Check if a file should be skipped during analysis"""
        skip_patterns = ['node_modules', '.venv', 'venv', '__pycache__', '.git', 'dist', 'build']
        return any(pattern in str(file_path) for pattern in skip_patterns)
    
    async def analyze_error(self, error: Error) -> ErrorAnalysis:
        """Analyze an error and determine root cause"""
        analysis = ErrorAnalysis(
            error=error,
            confidence=0.0
        )
        
        message_lower = error.message.lower()
        
        # Pattern matching
        for pattern_name, pattern_info in self.error_patterns.items():
            for pattern in pattern_info['patterns']:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    analysis.root_cause = pattern_info['root_cause']
                    analysis.suggested_fix = pattern_info['suggested_fix']
                    analysis.confidence = pattern_info['confidence']
                    break
            
            if analysis.root_cause:
                break
        
        # Generate fix command
        if analysis.suggested_fix:
            analysis.fix_command = await self._generate_fix_command(error, analysis)
        
        # Determine if manual intervention is needed
        if analysis.confidence < 0.7 or not analysis.fix_command:
            analysis.requires_manual_intervention = True
        
        self.error_analyses[error.id] = analysis
        
        logger.info(f"📊 Error analysis: {analysis.root_cause} (confidence: {analysis.confidence})")
        return analysis
    
    async def _generate_fix_command(self, error: Error, analysis: ErrorAnalysis) -> Optional[str]:
        """Generate a fix command based on error analysis"""
        suggested_fix = analysis.suggested_fix
        message = error.message
        
        if suggested_fix == 'install_dependency':
            # Extract package name
            match = re.search(r"'([^']+)'|\"([^\"]+)\"|module\s+(\S+)", message, re.IGNORECASE)
            if match:
                package = match.group(1) or match.group(2) or match.group(3)
                
                # Determine package manager
                if error.component and 'python' in error.component.lower():
                    return f"pip3 install {package}"
                else:
                    return f"npm install {package}"
        
        elif suggested_fix == 'start_service':
            message_lower = message.lower()
            if 'redis' in message_lower:
                return "sudo systemctl start redis-server || redis-server --daemonize yes"
            elif 'postgres' in message_lower:
                return "sudo systemctl start postgresql"
            elif 'mongodb' in message_lower:
                return "sudo systemctl start mongod"
        
        elif suggested_fix == 'fix_permissions':
            if error.file:
                return f"chmod +x {error.file}"
        
        elif suggested_fix == 'kill_process_on_port':
            # Extract port number
            match = re.search(r'port\s+(\d+)|:(\d+)', message, re.IGNORECASE)
            if match:
                port = match.group(1) or match.group(2)
                return f"lsof -ti:{port} | xargs kill -9"
        
        return None
    
    async def apply_fix(self, analysis: ErrorAnalysis) -> Fix:
        """Apply a fix for an analyzed error"""
        fix_id = f"fix_{analysis.error.id}_{int(datetime.now().timestamp())}"
        fix = Fix(
            id=fix_id,
            error_id=analysis.error.id,
            command=analysis.fix_command or ""
        )
        
        if not analysis.fix_command:
            logger.warning(f"⚠️ No fix command available for error {analysis.error.id}")
            return fix
        
        try:
            logger.info(f"🔧 Applying fix: {analysis.fix_command}")
            
            process = await asyncio.create_subprocess_shell(
                analysis.fix_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=300)
            
            if process.returncode == 0:
                logger.info("✅ Fix applied successfully")
                fix.success = True
            else:
                logger.error(f"❌ Fix failed: {stderr.decode()}")
                fix.error_message = stderr.decode()
        
        except asyncio.TimeoutError:
            logger.error("❌ Fix command timed out")
            fix.error_message = "Command timed out"
        except Exception as e:
            logger.error(f"❌ Error applying fix: {e}")
            fix.error_message = str(e)
        
        self.applied_fixes[fix_id] = fix
        return fix
    
    async def validate_fix(self, fix: Fix) -> bool:
        """Validate that a fix resolved the error"""
        error = self.detected_errors.get(fix.error_id)
        if not error:
            return False
        
        # Re-run detection for the specific error type
        if error.source == ErrorSource.SYNTAX:
            errors = await self._check_syntax_errors()
            fix.validated = not any(e.file == error.file for e in errors)
        elif error.source == ErrorSource.DEPENDENCY:
            errors = await self._check_dependencies()
            fix.validated = not any(e.component == error.component for e in errors)
        elif error.source == ErrorSource.TEST:
            errors = await self._run_tests()
            fix.validated = len(errors) == 0
        else:
            # For other types, assume validated if fix was successful
            fix.validated = fix.success
        
        logger.info(f"✅ Fix validation: {'PASSED' if fix.validated else 'FAILED'}")
        return fix.validated
    
    async def auto_heal_cycle(self):
        """Run one cycle of auto-healing"""
        logger.info("🏥 Starting auto-healing cycle")
        
        # Detect errors
        errors = await self.detect_errors()
        
        if not errors:
            logger.info("✅ No errors detected")
            return
        
        # Analyze and fix errors
        for error in errors:
            logger.info(f"🔍 Processing error: {error.message[:100]}")
            
            # Analyze error
            analysis = await self.analyze_error(error)
            
            if analysis.requires_manual_intervention:
                logger.warning(f"⚠️ Error requires manual intervention: {error.id}")
                continue
            
            # Apply fix
            fix = await self.apply_fix(analysis)
            
            if fix.success:
                # Validate fix
                validated = await self.validate_fix(fix)
                if validated:
                    logger.info(f"✅ Error {error.id} resolved successfully")
                else:
                    logger.warning(f"⚠️ Fix applied but error persists: {error.id}")
    
    async def continuous_improvement_cycle(self):
        """Run one cycle of continuous improvement"""
        logger.info("📈 Starting continuous improvement cycle")
        
        # Analyze code quality
        metrics = await self._analyze_code_metrics()
        
        logger.info(f"📊 Code metrics: {metrics}")
        
        # Identify optimization opportunities
        opportunities = await self._identify_optimizations(metrics)
        
        if opportunities:
            logger.info(f"💡 Found {len(opportunities)} optimization opportunities")
            for opp in opportunities:
                logger.info(f"  - {opp}")
    
    async def _analyze_code_metrics(self) -> Dict[str, Any]:
        """Analyze code quality metrics"""
        metrics = {
            'total_files': 0,
            'total_lines': 0,
            'python_files': 0,
            'js_files': 0,
            'avg_file_size': 0
        }
        
        file_sizes = []
        
        for file_path in self.project_root.rglob('*'):
            if not file_path.is_file() or self._should_skip_file(file_path):
                continue
            
            metrics['total_files'] += 1
            
            try:
                with open(file_path, 'r') as f:
                    lines = len(f.readlines())
                    metrics['total_lines'] += lines
                    file_sizes.append(lines)
                
                if file_path.suffix == '.py':
                    metrics['python_files'] += 1
                elif file_path.suffix in ['.js', '.ts', '.jsx', '.tsx']:
                    metrics['js_files'] += 1
            except Exception:
                pass
        
        if file_sizes:
            metrics['avg_file_size'] = sum(file_sizes) / len(file_sizes)
        
        return metrics
    
    async def _identify_optimizations(self, metrics: Dict[str, Any]) -> List[str]:
        """Identify optimization opportunities"""
        opportunities = []
        
        if metrics['avg_file_size'] > 500:
            opportunities.append("Consider splitting large files into smaller modules")
        
        if metrics['total_files'] > 100 and metrics['python_files'] == 0:
            opportunities.append("Consider adding Python backend components")
        
        return opportunities
    
    async def run(self):
        """Main run loop"""
        self.running = True
        logger.info("🚀 Autonomous Development v2.0 running...")
        
        try:
            while self.running:
                # Run auto-healing cycle
                await self.auto_heal_cycle()
                
                # Run continuous improvement cycle every 10 cycles
                if datetime.now().minute % 10 == 0:
                    await self.continuous_improvement_cycle()
                
                # Sleep for 5 minutes before next cycle
                await asyncio.sleep(300)
        
        except Exception as e:
            logger.error(f"❌ Error in main loop: {e}")
        finally:
            logger.info("🛑 Autonomous Development v2.0 stopped")
    
    async def shutdown(self):
        """Gracefully shutdown"""
        logger.info("🛑 Shutting down Autonomous Development v2.0...")
        self.running = False
        logger.info("✅ Shutdown complete")


# Main entry point
async def main():
    project_root = Path(__file__).parent.parent
    auto_dev = AutonomousDevelopmentV2(project_root)
    await auto_dev.run()


if __name__ == '__main__':
    asyncio.run(main())
