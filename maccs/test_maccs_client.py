import unittest
import os
import json
import subprocess
import sqlite3
from unittest.mock import patch, MagicMock

from maccs_client import MACCSClientV3

class TestMACCSClientV3(unittest.TestCase):
    def setUp(self):
        self.test_repo_path = "/tmp/test_repo"
        self.test_db_path = os.path.join(self.test_repo_path, "maccs/test_coordination.db")
        self.manus_id = "manus_6"

        os.makedirs(os.path.join(self.test_repo_path, "maccs"), exist_ok=True)
        subprocess.run(["git", "init"], cwd=self.test_repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=self.test_repo_path, capture_output=True)
        subprocess.run(["git", "config", "user.name", "Test User"], cwd=self.test_repo_path, capture_output=True)
        with open(os.path.join(self.test_repo_path, "README.md"), "w") as f:
            f.write("Test Repo")
        subprocess.run(["git", "add", "README.md"], cwd=self.test_repo_path, capture_output=True)
        subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=self.test_repo_path, capture_output=True)

        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        
        self.client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        self.client.update_capabilities(
            skills=["python", "typescript", "javascript", "testing", "documentation", "git"],
            specialization="QA & Coordination",
            max_concurrent_tasks=2,
            preferred_task_types=["bug_fix", "testing", "documentation"]
        )

    def tearDown(self):
        self.client.close()
        if os.path.exists(self.test_repo_path):
            subprocess.run(["rm", "-rf", self.test_repo_path])

    def test_db_connection_error(self):
        with patch("sqlite3.connect", side_effect=sqlite3.Error("Test DB Error")):
            client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
            self.assertIsNone(client.conn)

    @patch("sqlite3.connect")
    def test_initialize_db_error(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("Init DB Error")
        mock_connect.return_value = mock_conn
        client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        # No direct assertion, but ensures no crash

    @patch("sqlite3.connect")
    def test_send_message_error(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.Error("Send Message Error")
        mock_connect.return_value = mock_conn
        client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        msg_id = client.send_message("manus_2", "TEST_MSG", {"data": "test"})
        self.assertIsNone(msg_id)

    @patch("sqlite3.connect")
    def test_get_unread_messages_error(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.cursor.return_value.execute.side_effect = sqlite3.Error("Get Unread Error")
        mock_connect.return_value = mock_conn
        client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        messages = client.get_unread_messages()
        self.assertEqual(messages, [])

    @patch("sqlite3.connect")
    def test_post_task_error(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.Error("Post Task Error")
        mock_connect.return_value = mock_conn
        client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        task_id = client.post_task("Test Task", "Desc", ["python"])
        self.assertIsNone(task_id)

    @patch("sqlite3.connect")
    def test_send_heartbeat_error(self, mock_connect):
        mock_conn = MagicMock()
        mock_conn.execute.side_effect = sqlite3.Error("Heartbeat Error")
        mock_connect.return_value = mock_conn
        client = MACCSClientV3(self.manus_id, self.test_repo_path, db_path="maccs/test_coordination.db")
        client.send_heartbeat()
        # No direct assertion, but ensures no crash

    def test_git_sync_and_backup_failure(self):
        with patch("subprocess.run", side_effect=subprocess.CalledProcessError(1, "git pull", stderr=b"Git pull failed")):
            result = self.client.git_sync_and_backup()
            self.assertFalse(result)

    def test_discover_best_task_no_tasks(self):
        best_task = self.client.discover_best_task()
        self.assertIsNone(best_task)

    def test_discover_best_task_scoring(self):
        self.client.post_task("Bug Fix: Python Script", "Fix f-string error", ["python", "debugging"], "HIGH")
        self.client.post_task("Frontend UI Improvement", "Refactor CSS", ["css", "frontend"], "NORMAL")
        self.client.post_task("Critical Testing Task", "Perform E2E tests", ["testing", "python"], "URGENT")
        best_task = self.client.discover_best_task()
        self.assertEqual(best_task["title"], "Critical Testing Task")

if __name__ == '__main__':
    unittest.main()
