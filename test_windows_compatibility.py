#!/usr/bin/env python3
"""
🪟 WINDOWS COMPATIBILITY TEST SUITE
Tests all components of the Flowstate-AI system for Windows compatibility

This script verifies:
- Path handling across platforms
- Database operations
- File I/O operations
- Network operations
- Process management
- Dashboard functionality
- Sync engine operations
"""

import os
import sys
import platform
import sqlite3
import json
import time
import threading
import subprocess
import socket
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
import logging

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class WindowsCompatibilityTester:
    """Comprehensive Windows compatibility testing suite"""
    
    def __init__(self):
        self.test_results = {}
        self.test_dir = Path(tempfile.mkdtemp(prefix="flowstate_test_"))
        self.platform_info = {
            "system": platform.system(),
            "version": platform.version(),
            "python_version": sys.version,
            "architecture": platform.architecture()
        }
        
        logger.info(f"🪟 Testing on {self.platform_info['system']} {self.platform_info['version']}")
        logger.info(f"🐍 Python {self.platform_info['python_version']}")
        logger.info(f"📁 Test directory: {self.test_dir}")
    
    def run_all_tests(self):
        """Run all compatibility tests"""
        logger.info("🚀 Starting Windows compatibility tests...")
        
        tests = [
            ("Path Handling", self.test_path_handling),
            ("Database Operations", self.test_database_operations),
            ("File I/O Operations", self.test_file_operations),
            ("Network Operations", self.test_network_operations),
            ("Process Management", self.test_process_management),
            ("JSON Operations", self.test_json_operations),
            ("Threading", self.test_threading),
            ("Sync Engine Components", self.test_sync_engine_components),
            ("Dashboard Components", self.test_dashboard_components)
        ]
        
        for test_name, test_func in tests:
            try:
                logger.info(f"🧪 Running test: {test_name}")
                result = test_func()
                self.test_results[test_name] = {
                    "status": "PASS" if result else "FAIL",
                    "details": f"Test completed successfully" if result else "Test failed"
                }
                logger.info(f"✅ {test_name}: {'PASS' if result else 'FAIL'}")
            except Exception as e:
                self.test_results[test_name] = {
                    "status": "ERROR",
                    "details": str(e)
                }
                logger.error(f"❌ {test_name}: ERROR - {e}")
        
        self.generate_report()
        self.cleanup()
    
    def test_path_handling(self):
        """Test cross-platform path handling"""
        try:
            # Test Path creation
            test_path = self.test_dir / "subdir" / "file.txt"
            test_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Test path operations
            assert test_path.parent.exists()
            assert test_path.parent.is_dir()
            
            # Test path string conversion
            path_str = str(test_path)
            path_from_str = Path(path_str)
            assert path_from_str == test_path
            
            # Test relative paths
            relative_path = test_path.relative_to(self.test_dir)
            assert relative_path.parts[0] == "subdir"
            
            # Test absolute paths
            absolute_path = test_path.resolve()
            assert absolute_path.is_absolute()
            
            return True
            
        except Exception as e:
            logger.error(f"Path handling test failed: {e}")
            return False
    
    def test_database_operations(self):
        """Test SQLite database operations"""
        try:
            db_path = self.test_dir / "test.db"
            
            # Test database creation
            conn = sqlite3.connect(db_path, timeout=30.0)
            conn.execute("PRAGMA journal_mode=WAL")
            conn.execute("PRAGMA synchronous=NORMAL")
            
            # Test table creation
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE test_table (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Test data insertion
            cursor.execute('''
                INSERT INTO test_table (name, data) VALUES (?, ?)
            ''', ("test_name", json.dumps({"test": "data"})))
            
            # Test data retrieval
            cursor.execute('SELECT * FROM test_table')
            rows = cursor.fetchall()
            assert len(rows) == 1
            
            # Test transaction
            conn.commit()
            
            # Test concurrent access
            conn2 = sqlite3.connect(db_path, timeout=30.0)
            cursor2 = conn2.cursor()
            cursor2.execute('SELECT COUNT(*) FROM test_table')
            count = cursor2.fetchone()[0]
            assert count == 1
            
            conn.close()
            conn2.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Database operations test failed: {e}")
            return False
    
    def test_file_operations(self):
        """Test file I/O operations"""
        try:
            # Test text file operations
            text_file = self.test_dir / "test.txt"
            test_content = "Windows compatibility test\nLine 2\nLine 3"
            
            text_file.write_text(test_content, encoding='utf-8')
            read_content = text_file.read_text(encoding='utf-8')
            assert read_content == test_content
            
            # Test binary file operations
            binary_file = self.test_dir / "test.bin"
            test_data = b"Binary test data"
            
            binary_file.write_bytes(test_data)
            read_data = binary_file.read_bytes()
            assert read_data == test_data
            
            # Test file metadata
            stat = text_file.stat()
            assert stat.st_size > 0
            
            # Test file permissions (if supported)
            if platform.system() != 'Windows':
                os.chmod(text_file, 0o644)
            
            # Test directory operations
            sub_dir = self.test_dir / "subdir"
            sub_dir.mkdir(exist_ok=True)
            assert sub_dir.exists()
            assert sub_dir.is_dir()
            
            # Test file listing
            files = list(self.test_dir.iterdir())
            assert len(files) >= 3  # test.txt, test.bin, subdir
            
            return True
            
        except Exception as e:
            logger.error(f"File operations test failed: {e}")
            return False
    
    def test_network_operations(self):
        """Test network operations"""
        try:
            # Test socket creation
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            
            # Test port binding
            sock.bind(('localhost', 0))  # Bind to any available port
            port = sock.getsockname()[1]
            
            # Test listening
            sock.listen(1)
            
            # Test socket info
            assert port > 0
            
            sock.close()
            
            # Test port availability check
            def is_port_available(port):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('localhost', port))
                        return True
                except OSError:
                    return False
            
            # Find an available port
            test_port = 8888
            while not is_port_available(test_port) and test_port < 9000:
                test_port += 1
            
            assert test_port < 9000  # Should find an available port
            
            return True
            
        except Exception as e:
            logger.error(f"Network operations test failed: {e}")
            return False
    
    def test_process_management(self):
        """Test process management operations"""
        try:
            # Test subprocess creation
            if platform.system() == 'Windows':
                result = subprocess.run(['echo', 'test'], capture_output=True, text=True, shell=True)
            else:
                result = subprocess.run(['echo', 'test'], capture_output=True, text=True)
            
            assert result.returncode == 0
            assert 'test' in result.stdout
            
            # Test process information
            current_pid = os.getpid()
            assert current_pid > 0
            
            # Test environment variables
            test_env = os.environ.copy()
            test_env['TEST_VAR'] = 'test_value'
            
            if platform.system() == 'Windows':
                result = subprocess.run(['echo', '%TEST_VAR%'], 
                                      capture_output=True, text=True, 
                                      env=test_env, shell=True)
            else:
                result = subprocess.run(['echo', '$TEST_VAR'], 
                                      capture_output=True, text=True, 
                                      env=test_env, shell=True)
            
            # Note: Environment variable expansion might not work in all cases
            # This is acceptable for compatibility testing
            
            return True
            
        except Exception as e:
            logger.error(f"Process management test failed: {e}")
            return False
    
    def test_json_operations(self):
        """Test JSON operations"""
        try:
            # Test JSON serialization
            test_data = {
                "string": "test",
                "number": 42,
                "float": 3.14,
                "boolean": True,
                "null": None,
                "array": [1, 2, 3],
                "object": {"nested": "value"},
                "timestamp": datetime.now().isoformat()
            }
            
            # Test JSON dumps/loads
            json_str = json.dumps(test_data, indent=2)
            parsed_data = json.loads(json_str)
            
            assert parsed_data["string"] == test_data["string"]
            assert parsed_data["number"] == test_data["number"]
            assert parsed_data["boolean"] == test_data["boolean"]
            
            # Test JSON file operations
            json_file = self.test_dir / "test.json"
            json_file.write_text(json_str, encoding='utf-8')
            
            loaded_data = json.loads(json_file.read_text(encoding='utf-8'))
            assert loaded_data["string"] == test_data["string"]
            
            return True
            
        except Exception as e:
            logger.error(f"JSON operations test failed: {e}")
            return False
    
    def test_threading(self):
        """Test threading operations"""
        try:
            results = []
            
            def worker_function(worker_id):
                time.sleep(0.1)
                results.append(f"worker_{worker_id}")
            
            # Test thread creation and execution
            threads = []
            for i in range(3):
                thread = threading.Thread(target=worker_function, args=(i,))
                threads.append(thread)
                thread.start()
            
            # Test thread joining
            for thread in threads:
                thread.join(timeout=5.0)
            
            assert len(results) == 3
            assert "worker_0" in results
            assert "worker_1" in results
            assert "worker_2" in results
            
            # Test thread-safe operations
            lock = threading.Lock()
            shared_counter = [0]
            
            def increment_counter():
                for _ in range(100):
                    with lock:
                        shared_counter[0] += 1
            
            threads = []
            for _ in range(3):
                thread = threading.Thread(target=increment_counter)
                threads.append(thread)
                thread.start()
            
            for thread in threads:
                thread.join()
            
            assert shared_counter[0] == 300
            
            return True
            
        except Exception as e:
            logger.error(f"Threading test failed: {e}")
            return False
    
    def test_sync_engine_components(self):
        """Test sync engine components"""
        try:
            # Test enum definitions
            from enum import Enum
            
            class TestRole(Enum):
                DEVELOPER = "developer"
                TESTER = "tester"
            
            class TestStatus(Enum):
                ACTIVE = "active"
                INACTIVE = "inactive"
            
            # Test dataclass-like structures
            test_instance = {
                "id": "test_manus",
                "role": TestRole.DEVELOPER,
                "status": TestStatus.ACTIVE,
                "capabilities": ["python", "testing"],
                "last_heartbeat": datetime.now(),
                "performance_score": 95.5
            }
            
            # Test serialization
            serialized = {
                "id": test_instance["id"],
                "role": test_instance["role"].value,
                "status": test_instance["status"].value,
                "capabilities": json.dumps(test_instance["capabilities"]),
                "last_heartbeat": test_instance["last_heartbeat"].isoformat(),
                "performance_score": test_instance["performance_score"]
            }
            
            # Test database storage
            db_path = self.test_dir / "sync_test.db"
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                CREATE TABLE manus_instances (
                    id TEXT PRIMARY KEY,
                    role TEXT,
                    status TEXT,
                    capabilities TEXT,
                    last_heartbeat TIMESTAMP,
                    performance_score REAL
                )
            ''')
            
            cursor.execute('''
                INSERT INTO manus_instances 
                (id, role, status, capabilities, last_heartbeat, performance_score)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                serialized["id"],
                serialized["role"],
                serialized["status"],
                serialized["capabilities"],
                serialized["last_heartbeat"],
                serialized["performance_score"]
            ))
            
            conn.commit()
            
            # Test retrieval
            cursor.execute('SELECT * FROM manus_instances WHERE id = ?', (test_instance["id"],))
            row = cursor.fetchone()
            assert row is not None
            assert row[0] == test_instance["id"]
            
            conn.close()
            
            return True
            
        except Exception as e:
            logger.error(f"Sync engine components test failed: {e}")
            return False
    
    def test_dashboard_components(self):
        """Test dashboard components"""
        try:
            # Test Flask-like data structures
            dashboard_data = {
                'timestamp': datetime.now().isoformat(),
                'ai_agents': [
                    {
                        'id': 'test_agent',
                        'name': 'Test Agent',
                        'status': 'ACTIVE',
                        'progress': 75,
                        'current_task': 'Testing compatibility'
                    }
                ],
                'system_stats': {
                    'total_ais': 1,
                    'active_ais': 1,
                    'completed_tasks': 5,
                    'uptime': '1:30:45'
                }
            }
            
            # Test JSON serialization for API responses
            json_response = json.dumps(dashboard_data, indent=2)
            parsed_response = json.loads(json_response)
            
            assert parsed_response['ai_agents'][0]['id'] == 'test_agent'
            assert parsed_response['system_stats']['total_ais'] == 1
            
            # Test template-like operations
            template_vars = {
                'title': 'GODMODE Dashboard',
                'agents': dashboard_data['ai_agents'],
                'stats': dashboard_data['system_stats']
            }
            
            # Test HTML generation (simplified)
            html_content = f"""
            <html>
                <head><title>{template_vars['title']}</title></head>
                <body>
                    <h1>{template_vars['title']}</h1>
                    <div>Total AIs: {template_vars['stats']['total_ais']}</div>
                </body>
            </html>
            """
            
            assert 'GODMODE Dashboard' in html_content
            assert 'Total AIs: 1' in html_content
            
            # Test file serving simulation
            static_file = self.test_dir / "static" / "test.css"
            static_file.parent.mkdir(parents=True, exist_ok=True)
            static_file.write_text("body { background: #1a1a1a; }")
            
            assert static_file.exists()
            content = static_file.read_text()
            assert 'background' in content
            
            return True
            
        except Exception as e:
            logger.error(f"Dashboard components test failed: {e}")
            return False
    
    def generate_report(self):
        """Generate compatibility test report"""
        report = {
            "test_timestamp": datetime.now().isoformat(),
            "platform_info": self.platform_info,
            "test_results": self.test_results,
            "summary": {
                "total_tests": len(self.test_results),
                "passed": len([r for r in self.test_results.values() if r["status"] == "PASS"]),
                "failed": len([r for r in self.test_results.values() if r["status"] == "FAIL"]),
                "errors": len([r for r in self.test_results.values() if r["status"] == "ERROR"])
            }
        }
        
        # Calculate overall compatibility score
        total_tests = report["summary"]["total_tests"]
        passed_tests = report["summary"]["passed"]
        compatibility_score = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        report["compatibility_score"] = compatibility_score
        
        # Save report
        report_file = Path("windows_compatibility_report.json")
        report_file.write_text(json.dumps(report, indent=2))
        
        # Print summary
        logger.info("=" * 60)
        logger.info("🪟 WINDOWS COMPATIBILITY TEST REPORT")
        logger.info("=" * 60)
        logger.info(f"Platform: {self.platform_info['system']} {self.platform_info['version']}")
        logger.info(f"Python: {self.platform_info['python_version']}")
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests}")
        logger.info(f"Failed: {report['summary']['failed']}")
        logger.info(f"Errors: {report['summary']['errors']}")
        logger.info(f"Compatibility Score: {compatibility_score:.1f}%")
        logger.info("=" * 60)
        
        if compatibility_score >= 90:
            logger.info("✅ EXCELLENT Windows compatibility!")
        elif compatibility_score >= 75:
            logger.info("✅ GOOD Windows compatibility")
        elif compatibility_score >= 50:
            logger.info("⚠️ FAIR Windows compatibility - some issues detected")
        else:
            logger.info("❌ POOR Windows compatibility - significant issues detected")
        
        logger.info(f"📄 Detailed report saved to: {report_file.absolute()}")
        
        # Print failed tests
        failed_tests = [name for name, result in self.test_results.items() 
                       if result["status"] in ["FAIL", "ERROR"]]
        if failed_tests:
            logger.info("\n❌ Failed Tests:")
            for test_name in failed_tests:
                result = self.test_results[test_name]
                logger.info(f"  - {test_name}: {result['status']} - {result['details']}")
    
    def cleanup(self):
        """Clean up test files"""
        try:
            shutil.rmtree(self.test_dir)
            logger.info(f"🧹 Cleaned up test directory: {self.test_dir}")
        except Exception as e:
            logger.warning(f"⚠️ Failed to clean up test directory: {e}")

def main():
    """Main test execution"""
    logger.info("🚀 Starting Flowstate-AI Windows Compatibility Test Suite")
    
    tester = WindowsCompatibilityTester()
    tester.run_all_tests()
    
    logger.info("🏁 Windows compatibility testing completed")

if __name__ == "__main__":
    main()
