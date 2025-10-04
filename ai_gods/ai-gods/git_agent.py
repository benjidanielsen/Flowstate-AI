import logging
from typing import List, Dict, Any
from ai_gods.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class GitAgent(BaseAgent):
    """An agent specialized in Git operations."""

    def __init__(
        self,
        agent_id: str = "GitAgent",
        agent_name: str = "GitAgent",
        role: str = "Version Control Specialist",
        capabilities: List[str] = ["git_operations"],
        **kwargs: Any,
    ):
        super().__init__(agent_id, agent_name, role, capabilities, **kwargs)
        logger.info(f"{self.agent_name} initialized.")

    def _execute_git_command(self, command: str) -> str:
        """Executes a git command and returns the output."""
        full_command = f"git {command}"
        logger.info(f"Executing git command: {full_command}")
        output = self.run_terminal_command(full_command)
        if "fatal:" in output.lower() or "error:" in output.lower():
            logger.error(f"Git command failed: {output}")
        return output

    def commit_changes(self, message: str, add_all: bool = True) -> str:
        """Commits changes to the local repository."""
        if not self.can_auto_approve():
            return "Commit requires auto-approval, which is disabled."

        if add_all:
            self._execute_git_command("add .")

        commit_output = self._execute_git_command(f'commit -m "{message}"')
        logger.info(f"Commit successful: {commit_output}")
        return commit_output

    def push_changes(self, remote: str = "origin", branch: str = "main") -> str:
        """Pushes changes to a remote repository."""
        if not self.can_auto_approve():
            return "Push requires auto-approval, which is disabled."

        push_output = self._execute_git_command(f"push {remote} {branch}")
        logger.info(f"Push successful: {push_output}")
        return push_output

    def pull_changes(self, remote: str = "origin", branch: str = "main") -> str:
        """Pulls changes from a remote repository."""
        pull_output = self._execute_git_command(f"pull {remote} {branch}")
        logger.info(f"Pull successful: {pull_output}")
        return pull_output

    def process_message(self, message_data: Dict[str, Any]):
        """Processes messages for Git operations."""
        super().process_message(message_data)
        if message_data.get("type") == "task_assignment":
            payload = message_data.get("payload", {})
            action = payload.get("action")

            if action == "commit":
                commit_message = payload.get("message", "Automated commit by GitAgent")
                self.commit_changes(commit_message)
            elif action == "push":
                self.push_changes()
            elif action == "pull":
                self.pull_changes()
