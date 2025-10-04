from .base_agent import BaseAgent
from .git_agent import GitAgent

# Import other specialized agents as needed
# from .fixer_ai import FixerAI
# from .vscode_agent import VSCodeAgent


class ProjectManagerAgent(BaseAgent):
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
        self.git_agent = GitAgent(
            agent_id="git_agent_001",
            agent_name="GitAgent",
            role="Version Control Specialist",
            capabilities=["git_add", "git_commit", "git_push"],
        )
        # Instantiate other agents here
        # self.fixer_agent = FixerAI(...)
        # self.vscode_agent = VSCodeAgent(...)

    def delegate_task(self, task: dict):
        """Delegates a task to the appropriate specialized agent."""
        agent_name = task.get("agent")
        action = task.get("action")
        description = task.get("description")

        self.logger.info(f"Project Manager received task: {description}")

        # Simple routing logic
        if agent_name == "GitAgent" or action == "auto_publish":
            commit_message = f"Auto-publish: {description}"
            self.git_agent.auto_publish(commit_message)
        # Add more routing logic for other agents
        # elif agent_name == "FixerAI":
        #     self.fixer_agent.execute_task(task)
        # elif agent_name == "VSCodeAgent":
        #     self.vscode_agent.execute_task(task)
        else:
            self.logger.warning(f"No agent found to handle task: {description}")

        # After a significant task, we can decide to auto-publish
        if task.get("priority") in ["critical", "high"]:
            self.git_agent.auto_publish(f"Completed task: {description}")

    def execute_plan(self, plan: list[dict]):
        """Executes a plan of tasks."""
        for task in plan:
            self.delegate_task(task)
