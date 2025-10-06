#!/usr/bin/env python3
"""
🤖 VSCode Agent v1.0
⚡ GODMODE: Unlimited autonomous development authority
🎯 Mission: Interact with the VSCode environment, manage extensions, and configure settings.
"""

import asyncio
import json
import logging
import os
from pathlib import Path

from ai_gods.base_agent import BaseAgent
from ai_gods.logging_config import setup_logging
from ai_gods.vscode_agent_integration import VSCodeAgentIntegration

# Configure logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
logger = setup_logging("VSCodeAgent", "vscode_agent.log")


class VSCodeAgent(BaseAgent):
    """
    An agent dedicated to interacting with the VSCode environment.
    """

    def __init__(self):
        super().__init__(
            agent_id="vscode_agent",
            agent_name="VSCode Agent",
            role="Manages VSCode environment, settings, and extensions.",
            capabilities=["configure_sqltools", "manage_extensions"],
        )
        self.vscode_integration = VSCodeAgentIntegration()
        self.project_root = Path(__file__).parent.parent
        self.settings_file = self.project_root / ".vscode" / "settings.json"
        self.running = True

    async def configure_sqltools(self):
        """
        Automatically configure the SQLTools extension.
        """
        logger.info("Configuring SQLTools extension...")
        try:
            self.settings_file.parent.mkdir(exist_ok=True)

            if self.settings_file.exists():
                with open(self.settings_file, "r") as f:
                    settings = json.load(f)
            else:
                settings = {}

            # Add or update SQLTools settings
            settings["sqltools.connections"] = [
                {
                    "name": "Flowstate DB",
                    "driver": "SQLite",
                    "database": str(self.project_root / "godmode-state.db"),
                }
            ]
            settings["sqltools.useNodeRuntime"] = True

            with open(self.settings_file, "w") as f:
                json.dump(settings, f, indent=4)

            logger.info("✅ SQLTools configured successfully.")
            self.vscode_integration.notify_vscode(
                "SQLTools has been configured for the Flowstate database.", "info"
            )
            return True
        except Exception as e:
            logger.error(f"❌ Error configuring SQLTools: {e}")
            self.vscode_integration.notify_vscode(
                f"Error configuring SQLTools: {e}", "error"
            )
            return False

    async def run(self):
        """Main run loop for the VSCode Agent"""
        logger.info("🚀 VSCode Agent v1.0 starting main loop...")
        self.vscode_integration.register_agent(self.agent_id, "IDLE")

        # For now, the agent will just configure SQLTools on startup
        # In the future, this would listen for tasks from the Project Manager
        await self.configure_sqltools()

        while self.running:
            # In a real scenario, this would be a loop listening for tasks
            # from the project manager via Redis or another message queue.
            await asyncio.sleep(10)


async def main():
    agent = VSCodeAgent()
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
