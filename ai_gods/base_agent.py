import json
import logging
import os
import sqlite3
import subprocess
import threading
import time
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

import redis
from redis.client import PubSub

from ai_gods.godmode_config import is_full_autonomy_enabled
from ai_gods.logging_config import setup_logging

logger = setup_logging(__name__, "base_agent.log")


class BaseAgent:
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        capabilities: List[str],
        redis_host: str = "localhost",
        redis_port: int = 6379,
        db_path: str = ":memory:",
    ):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.role = role
        self.capabilities = capabilities
        self.redis_client: redis.StrictRedis = redis.StrictRedis(
            host=redis_host, port=redis_port, db=0, decode_responses=True
        )
        self.pubsub: PubSub = self.redis_client.pubsub()
        self.db_path = db_path
        self.db_connection: Optional[sqlite3.Connection] = None
        self.db_cursor: Optional[sqlite3.Cursor] = None
        self._initialize_db()
        self.is_running = False
        self.heartbeat_thread = None
        self.task_thread = None
        logger.info(
            f"Agent {self.agent_name} ({self.agent_id}) initialized with role {self.role}."
        )

    def can_auto_approve(self) -> bool:
        """Check if the agent has the authority to auto-approve actions."""
        return is_full_autonomy_enabled()

    def install_dependencies(self, dependencies: List[str]):
        if not self.can_auto_approve():
            logger.warning(
                f"Agent {self.agent_name} needs to install dependencies but lacks auto-approval."
            )
            return
        try:
            subprocess.check_call(["pip", "install", *dependencies])
            logger.info(
                f"Agent {self.agent_name} successfully installed dependencies: {dependencies}"
            )
        except subprocess.CalledProcessError as e:
            logger.error(f"Agent {self.agent_name} failed to install dependencies: {e}")

    def run_terminal_command(self, command: str) -> str:
        if not self.can_auto_approve():
            logger.warning(
                f"Agent {self.agent_name} needs to run a terminal command but lacks auto-approval."
            )
            return ""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, check=True
            )
            logger.info(f"Agent {self.agent_name} successfully ran command: {command}")
            return result.stdout
        except subprocess.CalledProcessError as e:
            logger.error(f"Agent {self.agent_name} failed to run command: {e}")
            return e.stderr

    def perform_file_operation(self, operation: str, file_path: str, content: str = ""):
        if not self.can_auto_approve():
            logger.warning(
                f"Agent {self.agent_name} needs to perform a file operation but lacks auto-approval."
            )
            return
        try:
            if operation == "write":
                with open(file_path, "w") as f:
                    f.write(content)
                logger.info(
                    f"Agent {self.agent_name} successfully wrote to file: {file_path}"
                )
            elif operation == "read":
                with open(file_path, "r") as f:
                    return f.read()
            else:
                logger.error(f"Unsupported file operation: {operation}")
        except Exception as e:
            logger.error(
                f"Agent {self.agent_name} failed to perform file operation: {e}"
            )

    def _initialize_db(self):
        os.makedirs(os.path.dirname(self.db_path) or ".", exist_ok=True)
        self.db_connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.db_cursor = self.db_connection.cursor()
        self.db_cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_state (
                agent_id TEXT PRIMARY KEY,
                agent_name TEXT,
                role TEXT,
                capabilities TEXT,
                status TEXT,
                last_heartbeat TEXT,
                current_task TEXT,
                progress INTEGER
            )
        """
        )
        self.db_connection.commit()
        self._update_agent_state(status="INITIALIZED", current_task="None", progress=0)

    def _update_agent_state(
        self,
        status: Optional[str] = None,
        current_task: Optional[str] = None,
        progress: Optional[int] = None,
    ):
        now = datetime.now().isoformat()
        update_fields: Dict[str, Any] = {
            "agent_name": self.agent_name,
            "role": self.role,
            "capabilities": json.dumps(self.capabilities),
            "last_heartbeat": now,
        }
        if status:
            update_fields["status"] = status
        if current_task:
            update_fields["current_task"] = current_task
        if progress is not None:
            update_fields["progress"] = progress

        if self.db_cursor:
            self.db_cursor.execute(
                "INSERT OR REPLACE INTO agent_state (agent_id, agent_name, role, capabilities, status, last_heartbeat, current_task, progress) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (
                    self.agent_id,
                    self.agent_name,
                    self.role,
                    json.dumps(self.capabilities),
                    update_fields.get("status", "ACTIVE"),
                    now,
                    update_fields.get("current_task", "None"),
                    update_fields.get("progress", 0),
                ),
            )
        if self.db_connection:
            self.db_connection.commit()

    def _send_heartbeat(self):
        while self.is_running:
            self._update_agent_state(status="ACTIVE")
            logger.debug(f"Agent {self.agent_name} sent heartbeat.")
            time.sleep(5)  # Heartbeat every 5 seconds

    def start(self):
        self.is_running = True
        self.heartbeat_thread = threading.Thread(target=self._send_heartbeat)
        self.heartbeat_thread.daemon = True
        self.heartbeat_thread.start()
        logger.info(f"Agent {self.agent_name} started.")

    def stop(self):
        self.is_running = False
        if self.heartbeat_thread:
            self.heartbeat_thread.join(timeout=1)
        if self.task_thread:
            self.task_thread.join(timeout=1)
        if self.db_connection:
            self.db_connection.close()
        logger.info(f"Agent {self.agent_name} stopped.")

    def publish_message(self, channel: str, message_type: str, payload: Dict[str, Any]):
        message = {
            "sender_id": self.agent_id,
            "sender_name": self.agent_name,
            "type": message_type,
            "payload": payload,
            "timestamp": datetime.now().isoformat(),
        }
        self.redis_client.publish(channel, json.dumps(message))
        logger.info(
            f"Agent {self.agent_name} published message to {channel}: {message_type}"
        )

    def subscribe_to_channel(
        self, channel: str, handler: Callable[[Dict[str, Any]], None]
    ):
        self.pubsub.subscribe(**{channel: handler})
        self.pubsub.run_in_thread(daemon=True)
        logger.info(f"Agent {self.agent_name} subscribed to channel {channel}.")

    def handle_message(self, message: Dict[str, Any]):
        # This method should be overridden by subclasses
        if message["type"] == "message":
            data = json.loads(message["data"])
            logger.info(
                f"Agent {self.agent_name} received message from {data['sender_name']} on {message['channel']}: {data['type']}"
            )
            # Process the message payload
            self.process_message(data)

    def process_message(self, message_data: Dict[str, Any]):
        # Placeholder for message processing logic
        logger.info(f"Agent {self.agent_name} processing message: {message_data}")
        # Example: update task based on message
        if message_data.get("type") == "task_assignment":
            task_description = message_data["payload"].get(
                "description", "No description"
            )
            self._update_agent_state(current_task=task_description, progress=0)
            logger.info(f"Agent {self.agent_name} assigned task: {task_description}")

    def run_task(self, task_function: Callable[..., Any], *args: Any, **kwargs: Any):
        # This method can be used to run a task in a separate thread
        self.task_thread = threading.Thread(
            target=task_function, args=args, kwargs=kwargs
        )
        self.task_thread.daemon = True
        self.task_thread.start()
        logger.info(f"Agent {self.agent_name} started a background task.")

    def get_agent_state(
        self, agent_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if agent_id is None:
            agent_id = self.agent_id
        if self.db_cursor:
            self.db_cursor.execute(
                "SELECT * FROM agent_state WHERE agent_id = ?", (agent_id,)
            )
            if row := self.db_cursor.fetchone():
                # Convert row to dictionary for easier access
                columns = [description[0] for description in self.db_cursor.description]
                return dict(zip(columns, row))

    def get_all_agent_states(self) -> List[Dict[str, Any]]:
        if not self.db_cursor:
            return []
        self.db_cursor.execute("SELECT * FROM agent_state")
        rows = self.db_cursor.fetchall()
        agents = []
        for row in rows:
            columns = [description[0] for description in self.db_cursor.description]
            agents.append(dict(zip(columns, row)))
        return agents


# Example Usage (for testing purposes)
if __name__ == "__main__":
    # Ensure Redis is running before executing this example
    # sudo systemctl start redis-server

    # Agent 1
    agent1 = BaseAgent(
        agent_id="agent_001",
        agent_name="Alice",
        role="Project Manager",
        capabilities=["planning", "coordination"],
        db_path="/tmp/agent_state.db",  # Use a temporary file for example
    )
    agent1.start()

    # Agent 2
    agent2 = BaseAgent(
        agent_id="agent_002",
        agent_name="Bob",
        role="Backend Developer",
        capabilities=["python", "database"],
        db_path="/tmp/agent_state.db",  # Share the same DB for visibility
    )
    agent2.start()

    # Agent 3 (subscribes to a channel and processes messages)
    class TestAgent(BaseAgent):
        def __init__(self, *args: Any, **kwargs: Any):
            super().__init__(*args, **kwargs)
            self.subscribe_to_channel("tasks", self.handle_message)

        def process_message(self, message_data: Dict[str, Any]):
            super().process_message(message_data)
            if message_data.get("type") == "task_assignment":
                task_description = message_data["payload"].get(
                    "description", "No description"
                )
                logger.info(
                    f"TestAgent {self.agent_name} is now working on: {task_description}"
                )
                # Simulate work
                for i in range(1, 11):
                    time.sleep(0.5)
                    self._update_agent_state(progress=i * 10)
                self._update_agent_state(
                    status="COMPLETED", current_task="None", progress=100
                )
                logger.info(
                    f"TestAgent {self.agent_name} completed task: {task_description}"
                )

    test_agent = TestAgent(
        agent_id="agent_003",
        agent_name="Charlie",
        role="QA Tester",
        capabilities=["testing", "debugging"],
        db_path="/tmp/agent_state.db",
    )
    test_agent.start()

    time.sleep(2)  # Give agents time to start and send initial heartbeats

    # Project Manager (agent1) assigns a task to Charlie (agent_003)
    agent1.publish_message(
        channel="tasks",
        message_type="task_assignment",
        payload={
            "assignee_id": "agent_003",
            "description": "Implement user authentication module",
        },
    )

    time.sleep(10)  # Allow Charlie to process the task

    # Check states
    logger.info("\n--- Current Agent States ---")
    for agent_state in agent1.get_all_agent_states():
        logger.info(agent_state)

    # Stop agents
    agent1.stop()
    agent2.stop()
    test_agent.stop()

    logger.info("Example finished.")
