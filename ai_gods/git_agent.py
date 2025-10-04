import subprocess

from .base_agent import BaseAgent


class GitAgent(BaseAgent):
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        role: str,
        capabilities: list[str],
        redis_host: str = "localhost",
        redis_port: int = 6379,
        db_path: str = ":memory:",
    ):
        super().__init__(
            agent_id, agent_name, role, capabilities, redis_host, redis_port, db_path
        )

    def add(self, files: list[str]):
        """Stages the specified files."""
        if not self.can_auto_approve():
            self.logger.warning(
                f"Agent {self.agent_name} needs to stage files but lacks auto-approval."
            )
            return
        command = ["git", "add"] + files
        self.run_terminal_command(" ".join(command))

    def commit(self, message: str):
        """Commits the staged changes."""
        if not self.can_auto_approve():
            self.logger.warning(
                f"Agent {self.agent_name} needs to commit changes but lacks auto-approval."
            )
            return
        command = ["git", "commit", "-m", f'"{message}"']
        self.run_terminal_command(" ".join(command))

    def push(self):
        """Pushes the committed changes to the remote repository."""
        if not self.can_auto_approve():
            self.logger.warning(
                f"Agent {self.agent_name} needs to push changes but lacks auto-approval."
            )
            return
        self.run_terminal_command("git push")

    def auto_publish(self, commit_message: str):
        """Adds all changes, commits, and pushes to the repository."""
        self.add(["."])
        self.commit(commit_message)
        self.push()
