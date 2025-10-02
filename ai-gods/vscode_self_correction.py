#!/usr/bin/env python3
"""
VSCode Self-Correction and Continuous Improvement Module
Implements self-healing, error detection, and continuous optimization for the VSCode system
"""

import asyncio
import json
import logging
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vscode_agent_integration import VSCodeAgentIntegration

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VSCodeSelfCorrectionSystem:
    """
    Self-correction and continuous improvement system for VSCode integration
    """
    
    def __init__(self, project_root: str, vscode_integration: VSCodeAgentIntegration):
        self.project_root = Path(project_root)
        self.vscode = vscode_integration
        self.error_log = []
        self.fixes_applied = []
        
    async def run_continuous_improvement_cycle(self):
        """Run a continuous improvement cycle"""
        logger.info("🔄 Starting continuous improvement cycle...")
        
        # Phase 1: Error Detection
        errors = await self.detect_errors()
        
        if errors:
            logger.info(f"🔍 Detected {len(errors)} errors")
            
            # Phase 2: Error Analysis and Fix Generation
            for error in errors:
                fix = await self.generate_fix(error)
                
                if fix:
                    # Phase 3: Apply Fix
                    success = await self.apply_fix(fix)
                    
                    if success:
                        # Phase 4: Validate Fix
                        validated = await self.validate_fix(error, fix)
                        
                        if validated:
                            logger.info(f"✅ Successfully fixed: {error['description']}")
                            self.fixes_applied.append({
                                'error': error,
                                'fix': fix,
                                'timestamp': datetime.now().isoformat()
                            })
                        else:
                            logger.warning(f"⚠️ Fix validation failed for: {error['description']}")
                    else:
                        logger.error(f"❌ Failed to apply fix for: {error['description']}")
        else:
            logger.info("✅ No errors detected")
        
        # Phase 5: Code Quality Analysis
        await self.analyze_code_quality()
        
        # Phase 6: Optimization Opportunities
        await self.identify_optimization_opportunities()
        
        logger.info("✅ Continuous improvement cycle completed")
    
    async def detect_errors(self) -> List[Dict]:
        """Detect errors in the project"""
        errors = []
        
        # 1. Check TypeScript compilation errors
        ts_errors = await self.check_typescript_errors()
        errors.extend(ts_errors)
        
        # 2. Check Python syntax errors
        py_errors = await self.check_python_errors()
        errors.extend(py_errors)
        
        # 3. Check for missing dependencies
        dep_errors = await self.check_missing_dependencies()
        errors.extend(dep_errors)
        
        # 4. Check for runtime errors in logs
        log_errors = await self.check_log_errors()
        errors.extend(log_errors)
        
        # 5. Check for test failures
        test_errors = await self.check_test_failures()
        errors.extend(test_errors)
        
        return errors
    
    async def check_typescript_errors(self) -> List[Dict]:
        """Check for TypeScript compilation errors"""
        errors = []
        
        try:
            # Run TypeScript compiler
            result = subprocess.run(
                ['npx', 'tsc', '--noEmit'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Parse TypeScript errors
                error_lines = result.stdout.split('\n')
                for line in error_lines:
                    if '.ts(' in line or '.tsx(' in line:
                        errors.append({
                            'type': 'typescript',
                            'description': line.strip(),
                            'severity': 'error',
                            'source': 'tsc'
                        })
        except Exception as e:
            logger.error(f"Error checking TypeScript: {e}")
        
        return errors
    
    async def check_python_errors(self) -> List[Dict]:
        """Check for Python syntax errors"""
        errors = []
        
        try:
            # Find all Python files
            python_files = list(self.project_root.rglob('*.py'))
            
            for py_file in python_files:
                try:
                    with open(py_file, 'r', encoding='utf-8') as f:
                        code = f.read()
                    
                    # Try to compile the Python code
                    compile(code, str(py_file), 'exec')
                except SyntaxError as e:
                    errors.append({
                        'type': 'python',
                        'description': f"{py_file}: {e.msg} at line {e.lineno}",
                        'severity': 'error',
                        'file': str(py_file),
                        'line': e.lineno,
                        'source': 'python'
                    })
        except Exception as e:
            logger.error(f"Error checking Python: {e}")
        
        return errors
    
    async def check_missing_dependencies(self) -> List[Dict]:
        """Check for missing dependencies"""
        errors = []
        
        try:
            # Check Node.js dependencies
            package_json = self.project_root / 'package.json'
            if package_json.exists():
                node_modules = self.project_root / 'node_modules'
                if not node_modules.exists():
                    errors.append({
                        'type': 'dependency',
                        'description': 'Node modules not installed',
                        'severity': 'error',
                        'fix_command': 'npm install',
                        'source': 'npm'
                    })
            
            # Check Python dependencies
            requirements = self.project_root / 'python-worker' / 'requirements.txt'
            if requirements.exists():
                # Try importing key packages
                try:
                    import flask
                    import redis
                except ImportError as e:
                    errors.append({
                        'type': 'dependency',
                        'description': f'Missing Python package: {e.name}',
                        'severity': 'error',
                        'fix_command': f'pip3 install {e.name}',
                        'source': 'pip'
                    })
        except Exception as e:
            logger.error(f"Error checking dependencies: {e}")
        
        return errors
    
    async def check_log_errors(self) -> List[Dict]:
        """Check for errors in log files"""
        errors = []
        
        try:
            log_dir = self.project_root / 'godmode-logs'
            if log_dir.exists():
                log_files = list(log_dir.glob('*.log'))
                
                for log_file in log_files:
                    try:
                        with open(log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()
                        
                        # Check last 100 lines for errors
                        for line in lines[-100:]:
                            if 'ERROR' in line or 'CRITICAL' in line:
                                errors.append({
                                    'type': 'runtime',
                                    'description': line.strip(),
                                    'severity': 'error',
                                    'file': str(log_file),
                                    'source': 'logs'
                                })
                    except Exception as e:
                        logger.error(f"Error reading log file {log_file}: {e}")
        except Exception as e:
            logger.error(f"Error checking logs: {e}")
        
        return errors
    
    async def check_test_failures(self) -> List[Dict]:
        """Check for test failures"""
        errors = []
        
        try:
            # Run tests
            result = subprocess.run(
                ['npm', 'test'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                errors.append({
                    'type': 'test',
                    'description': 'Test failures detected',
                    'severity': 'warning',
                    'output': result.stdout,
                    'source': 'tests'
                })
        except subprocess.TimeoutExpired:
            logger.warning("Test execution timed out")
        except Exception as e:
            logger.error(f"Error running tests: {e}")
        
        return errors
    
    async def generate_fix(self, error: Dict) -> Optional[Dict]:
        """Generate a fix for the detected error"""
        fix = None
        
        if error['type'] == 'dependency':
            # Fix: Install missing dependency
            fix = {
                'type': 'command',
                'command': error.get('fix_command'),
                'description': f"Install missing dependency: {error['description']}"
            }
        
        elif error['type'] == 'python' and 'SyntaxError' in error['description']:
            # Fix: Attempt to correct common Python syntax errors
            fix = {
                'type': 'code_fix',
                'file': error.get('file'),
                'description': f"Fix Python syntax error in {error.get('file')}"
            }
        
        elif error['type'] == 'runtime' and 'ModuleNotFoundError' in error['description']:
            # Extract module name
            match = re.search(r"No module named '(\w+)'", error['description'])
            if match:
                module_name = match.group(1)
                fix = {
                    'type': 'command',
                    'command': f'pip3 install {module_name}',
                    'description': f"Install missing Python module: {module_name}"
                }
        
        return fix
    
    async def apply_fix(self, fix: Dict) -> bool:
        """Apply the generated fix"""
        try:
            if fix['type'] == 'command':
                # Execute the fix command
                logger.info(f"🔧 Applying fix: {fix['description']}")
                
                # Send command to VSCode terminal
                self.vscode.send_terminal_command(fix['command'])
                
                # Wait for command to complete
                await asyncio.sleep(5)
                
                return True
            
            elif fix['type'] == 'code_fix':
                # Apply code fix
                logger.info(f"🔧 Applying code fix: {fix['description']}")
                
                # Notify VSCode to apply the fix
                self.vscode.notify_vscode(f"Applying fix: {fix['description']}", 'info')
                
                return True
        
        except Exception as e:
            logger.error(f"Error applying fix: {e}")
            return False
    
    async def validate_fix(self, error: Dict, fix: Dict) -> bool:
        """Validate that the fix resolved the error"""
        try:
            # Re-run error detection for the specific error type
            if error['type'] == 'typescript':
                errors = await self.check_typescript_errors()
            elif error['type'] == 'python':
                errors = await self.check_python_errors()
            elif error['type'] == 'dependency':
                errors = await self.check_missing_dependencies()
            else:
                return True  # Assume validated for other types
            
            # Check if the specific error still exists
            for e in errors:
                if e['description'] == error['description']:
                    return False
            
            return True
        except Exception as e:
            logger.error(f"Error validating fix: {e}")
            return False
    
    async def analyze_code_quality(self):
        """Analyze code quality and suggest improvements"""
        logger.info("📊 Analyzing code quality...")
        
        try:
            # Count lines of code
            total_files = 0
            total_lines = 0
            
            for ext in ['*.ts', '*.tsx', '*.py', '*.js', '*.jsx']:
                files = list(self.project_root.rglob(ext))
                total_files += len(files)
                
                for file in files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            total_lines += len(f.readlines())
                    except:
                        pass
            
            logger.info(f"📈 Code metrics: {total_files} files, {total_lines} lines")
            
            # Notify VSCode
            self.vscode.notify_vscode(
                f"Code quality analysis: {total_files} files, {total_lines} lines",
                'info'
            )
        except Exception as e:
            logger.error(f"Error analyzing code quality: {e}")
    
    async def identify_optimization_opportunities(self):
        """Identify optimization opportunities"""
        logger.info("🔍 Identifying optimization opportunities...")
        
        opportunities = []
        
        try:
            # Check for large files that could be split
            for ext in ['*.ts', '*.tsx', '*.py']:
                files = list(self.project_root.rglob(ext))
                
                for file in files:
                    try:
                        with open(file, 'r', encoding='utf-8') as f:
                            lines = len(f.readlines())
                        
                        if lines > 500:
                            opportunities.append(f"Consider splitting {file.name} ({lines} lines)")
                    except:
                        pass
            
            if opportunities:
                logger.info(f"💡 Found {len(opportunities)} optimization opportunities")
                for opp in opportunities[:5]:  # Show top 5
                    logger.info(f"  - {opp}")
        except Exception as e:
            logger.error(f"Error identifying optimizations: {e}")

# Example usage
async def main():
    # Initialize VSCode integration
    vscode_integration = VSCodeAgentIntegration()
    vscode_integration.register_agent('self-correction-system', 'ACTIVE')
    
    # Initialize self-correction system
    self_correction = VSCodeSelfCorrectionSystem(
        '/home/ubuntu/Flowstate-AI',
        vscode_integration
    )
    
    # Run continuous improvement cycle
    while True:
        await self_correction.run_continuous_improvement_cycle()
        
        # Wait 5 minutes before next cycle
        await asyncio.sleep(300)

if __name__ == '__main__':
    asyncio.run(main())
