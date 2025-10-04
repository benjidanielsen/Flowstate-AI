import logging
from typing import List, Dict, Any
from ai_gods.base_agent import BaseAgent

logger = logging.getLogger(__name__)


class VSCodeAgent(BaseAgent):
    """An agent specialized in managing the VS Code environment."""

    def __init__(
        self,
        agent_id: str = "VSCodeAgent",
        agent_name: str = "VSCodeAgent",
        role: str = "Environment Specialist",
        capabilities: List[str] = ["vscode_management"],
        **kwargs: Any,
    ):
        super().__init__(agent_id, agent_name, role, capabilities, **kwargs)
        logger.info(f"{self.agent_name} initialized.")

    def _execute_vscode_command(self, command: str) -> str:
        """Executes a VS Code command line command."""
        full_command = f"code --{command}"
        logger.info(f"Executing VS Code command: {full_command}")
        return self.run_terminal_command(full_command)

    def install_extension(self, extension_id: str) -> str:
        """Installs a VS Code extension."""
        if not self.can_auto_approve():
            return "Extension installation requires auto-approval, which is disabled."
        return self._execute_vscode_command(f"install-extension {extension_id}")

    def uninstall_extension(self, extension_id: str) -> str:
        """Uninstalls a VS Code extension."""
        if not self.can_auto_approve():
            return "Extension uninstallation requires auto-approval, which is disabled."
        return self._execute_vscode_command(f"uninstall-extension {extension_id}")

    def list_extensions(self) -> str:
        """Lists installed VS Code extensions."""
        return self._execute_vscode_command("list-extensions")

    def process_message(self, message_data: Dict[str, Any]):
        """Processes messages for VS Code operations."""
        super().process_message(message_data)
        if message_data.get("type") == "task_assignment":
            payload = message_data.get("payload", {})
            action = payload.get("action")

            if action == "install_extension":
                extension_id = payload.get("extension_id")
                if extension_id:
                    self.install_extension(extension_id)
            elif action == "uninstall_extension":
                extension_id = payload.get("extension_id")
                if extension_id:
                    self.uninstall_extension(extension_id)
            elif action == "list_extensions":
                self.list_extensions()
