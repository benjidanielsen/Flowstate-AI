import json
import logging
import time
from datetime import datetime
from base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProjectManagerAgent(BaseAgent):
    def __init__(self, agent_id: str, agent_name: str, capabilities: list, redis_host='localhost', redis_port=6379, db_path='/tmp/agent_state.db'):       super().__init__(agent_id, agent_name, \'Project Manager\', capabilities, redis_host, redis_port, db_path)
        self.pubsub.subscribe(**{\'agent_status_updates\': self.handle_message})
        logger.info(f"Project Manager Agent {self.agent_name} initialized.")

    def process_message(self, message_data: dict):
        # Override BaseAgent's process_message to handle PM-specific logic
        super().process_message(message_data) # Call base class for common processing

        message_type = message_data.get(\'type\')
        sender_id = message_data.get(\'sender_id\')
        sender_name = message_data.get(\'sender_name\')
        payload = message_data.get(\'payload\', {})

        if message_type == \'agent_status_update\':
            # Example: PM monitors agent status updates
            logger.info(f"PM received status update from {sender_name} ({sender_id}): {payload.get(\'status\')}, Task: {payload.get(\'current_task\')}, Progress: {payload.get(\'progress\')}%")
            # Here, PM could update its internal task tracking based on agent progress

        elif message_type == \'task_request\':
            # Example: An agent requests a task
            requested_task = payload.get(\'task_description\')
            logger.info(f"PM received task request from {sender_name}: {requested_task}")
            # PM would then delegate this task
            self.delegate_task(requested_task, sender_id) # For simplicity, delegate back to requester

        elif message_type == \'task_completion\':
            completed_task = payload.get(\'task_description\')
            logger.info(f"PM received task completion from {sender_name}: {completed_task}")
            # PM would mark task as complete and potentially assign new tasks

    def delegate_task(self, task_description: str, assignee_id: str):
        # In a real scenario, PM would choose the best agent based on capabilities and load
        # For now, we'll just publish to a generic \'tasks\' channel or directly to assignee
        self.publish_message(
            channel=\'tasks\',
            message_type=\'task_assignment\',
            payload={
                \'assignee_id\': assignee_id,
                \'description\': task_description,
                \'priority\': \'high\'
            }
        )
        logger.info(f"Project Manager delegated task \'{task_description}\' to {assignee_id}.")
        self._update_agent_state(current_task=f"Delegating: {task_description}", progress=50)

    def monitor_progress(self):
        # This method would typically run in a loop or be triggered by events
        # For now, it's a placeholder to show PM's monitoring capability
        logger.info(f"Project Manager {self.agent_name} is monitoring overall project progress.")
        all_agents_state = self.get_all_agent_states()
        for agent_state in all_agents_state:
            logger.info(f"Agent {agent_state.get(\'agent_name\')} ({agent_state.get(\'role\')}) - Status: {agent_state.get(\'status\')}, Task: {agent_state.get(\'current_task\')}, Progress: {agent_state.get(\'progress\')}%")
        self._update_agent_state(current_task="Monitoring agents", progress=100)

# Example Usage
if __name__ == \'__main__\':
    pm_agent = ProjectManagerAgent(
        agent_id=\'pm_001\',
        agent_name=\'Athena\',
        capabilities=[\'planning\', \'delegation\', \'monitoring\', \'risk_assessment\'],
        db_path=\'/tmp/agent_state.db\'
    )
    pm_agent.start()

    # Simulate another agent requesting a task
    class SimpleAgent(BaseAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.subscribe_to_channel(\'tasks\', self.handle_message)

        def request_task(self, task_description: str):
            self.publish_message(
                channel=\'agent_status_updates\', # PM listens on this channel for requests
                message_type=\'task_request\',
                payload={\'task_description\': task_description}
            )
            logger.info(f"Simple Agent {self.agent_name} requested task: {task_description}")

        def process_message(self, message_data: dict):
            super().process_message(message_data)
            if message_data.get(\'type\') == \'task_assignment\':
                task_description = message_data[
                    \'payload\'].get(\'description\', \'No description\')
                logger.info(
                    f"Simple Agent {self.agent_name} received task: {task_description}")
                # Simulate work
                for i in range(1, 6):
                    time.sleep(0.5)
                    self._update_agent_state(current_task=task_description, progress=i*20)
                self._update_agent_state(status=\'COMPLETED\', current_task=\'None\', progress=100)
                self.publish_message(
                    channel=\'agent_status_updates\',
                    message_type=\'task_completion\',
                    payload={\'task_description\': task_description}
                )
                logger.info(f"Simple Agent {self.agent_name} completed task: {task_description}")

    dev_agent = SimpleAgent(
        agent_id=\'dev_001\',
        agent_name=\'Hephaestus\',
        role=\'Developer\',
        capabilities=[\'coding\', \'debugging\'],
        db_path=\'/tmp/agent_state.db\'
    )
    dev_agent.start()

    time.sleep(2) # Give agents time to start

    dev_agent.request_task(\'Develop the user profile module\')

    time.sleep(10) # Allow task to be processed and completed

    pm_agent.monitor_progress()

    # Stop agents
    pm_agent.stop()
    dev_agent.stop()
    logger.info("Project Manager Agent example finished.")

