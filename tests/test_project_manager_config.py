import io
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_DIR = REPO_ROOT / "ai_gods"
if str(MODULE_DIR) not in sys.path:
    sys.path.insert(0, str(MODULE_DIR))

import project_manager_config  # type: ignore  # noqa: E402


class ProjectManagerConfigTests(unittest.TestCase):
    def setUp(self) -> None:
        self._original_env = {}

    def tearDown(self) -> None:
        for key, value in self._original_env.items():
            if value is None and key in os.environ:
                del os.environ[key]
            elif value is not None:
                os.environ[key] = value
        self._original_env.clear()

    def _setenv(self, key: str, value: str) -> None:
        self._original_env.setdefault(key, os.environ.get(key))
        os.environ[key] = value


    def test_load_project_manager_config_creates_directories(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            db_relative = "state/manager.db"
            log_relative = "logs/manager.log"
            self._setenv("GODMODE_DB_PATH", db_relative)
            self._setenv("GODMODE_PM_LOG_PATH", log_relative)
            self._setenv("GODMODE_REDIS_HOST", "redis.example")
            self._setenv("GODMODE_REDIS_PORT", "6380")
            self._setenv("GODMODE_REDIS_PASSWORD", "secret")

            config = project_manager_config.load_project_manager_config(project_root)

            self.assertEqual(config.redis_host, "redis.example")
            self.assertEqual(config.redis_port, 6380)
            self.assertEqual(config.redis_password, "secret")
            self.assertEqual(config.db_path, project_root / db_relative)
            self.assertEqual(config.log_path, project_root / log_relative)
            self.assertTrue(config.db_path.parent.exists())
            self.assertTrue(config.log_path.parent.exists())

    def test_invalid_port_falls_back_to_default(self) -> None:
        self._setenv("GODMODE_REDIS_PORT", "invalid")
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            capture = io.StringIO()
            original_stdout = sys.stdout
            try:
                sys.stdout = capture
                config = project_manager_config.load_project_manager_config(project_root)
            finally:
                sys.stdout = original_stdout

        self.assertIn("Invalid value", capture.getvalue())
        self.assertEqual(config.redis_port, 6379)


if __name__ == "__main__":
    unittest.main()

