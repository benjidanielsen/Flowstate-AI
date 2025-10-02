import json
import logging
import time
from datetime import datetime
from base_agent import BaseAgent

logger = logging.getLogger(__name__)

class ProjectManagerAgent(BaseAgent):
   def __init__(self, agent_id: str, agent_name: str, capabilities: list, redis_host=\'localhost\', redis_port=6379, db_path=\'/tmp/agent_state.db\'):
        self.pubsub.subscribe(**{'agent_status_updates': self.handle_message})
        logger.info(f"Project Manager Agent {self.agent_name} initialized.")

    def process_message(self, message_data: dict):
        super().process_message(message_data)
        message_type = message_data.get('type')
        sender_id = message_data.get('sender_id')
        sender_name = message_data.get('sender_name')
        payload = message_data.get('payload', {})

        if message_type == 'agent_status_update':
            logger.info(f"PM received status update from {sender_name} ({sender_id}): {payload.get('status')}, Task: {payload.get('current_task')}, Progress: {payload.get('progress')}% ")
        elif message_type == 'task_request':
            requested_task = payload.get('task_description')
            logger.info(f"PM received task request from {sender_name}: {requested_task}")
            # PM delegates the task back to the requesting agent
            self.delegate_task(requested_task, sender_id)
        elif message_type == 'task_completion':
            completed_task = payload.get('task_description')
            logger.info(f"PM received task completion from {sender_name}: {completed_task}")

    def delegate_task(self, task_description: str, assignee_id: str):
        # In a real scenario, PM would choose the best agent based on capabilities and load
        # For now, we'll publish directly to the assignee's channel (which is their agent_id)
        self.publish_message(
            channel=assignee_id, # Publish directly to the assignee's channel
            message_type='task_assignment',
            payload={
                'assignee_id': assignee_id,
                'description': task_description,
                'priority': 'high'
            }
        )
        logger.info(f"Project Manager delegated task '{task_description}' to {assignee_id}.")
        self._update_agent_state(current_task=f"Delegating: {task_description}", progress=50)

    def monitor_progress(self):
        logger.info(f"Project Manager {self.agent_name} is monitoring overall project progress.")
        all_agents_state = self.get_all_agent_states()
        for agent_state in all_agents_state:
            logger.info(f"Agent {agent_state.get('agent_name')} ({agent_state.get('role')}) - Status: {agent_state.get('status')}, Task: {agent_state.get('current_task')}, Progress: {agent_state.get('progress')}% ")
        self._update_agent_state(current_task="Monitoring agents", progress=100)

if __name__ == '__main__':
    pm_agent = ProjectManagerAgent(
        agent_id='pm_001',
        agent_name='Athena',
        capabilities=['planning', 'delegation', 'monitoring', 'risk_assessment'],
        db_path='/tmp/agent_state.db'
    )
    pm_agent.start()

    class SimpleAgent(BaseAgent):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # SimpleAgent should subscribe to its own agent_id channel to receive direct assignments
            self.subscribe_to_channel(self.agent_id, self.handle_message)

        def request_task(self, task_description: str):
            self.publish_message(
                channel='agent_status_updates', # PM listens on this channel for requests
                message_type='task_request',
                payload={'task_description': task_description}
            )
            logger.info(f"Simple Agent {self.agent_name} requested task: {task_description}")

        def process_message(self, message_data: dict):
            super().process_message(message_data)
            if message_data.get('type') == 'task_assignment':
                task_description = message_data['payload'].get('description', 'No description')
                logger.info(f"Simple Agent {self.agent_name} received task: {task_description}")
                # Simulate work
                for i in range(1, 6):
                    time.sleep(0.5)
                    self._update_agent_state(current_task=task_description, progress=i*20)
                self._update_agent_state(status='COMPLETED', current_task='None', progress=100)
                self.publish_message(
                    channel='agent_status_updates',
                    message_type='task_completion',
                    payload={'task_description': task_description}
                )
                logger.info(f"Simple Agent {self.agent_name} completed task: {task_description}")

    dev_agent = SimpleAgent(
        agent_id='dev_001',
        agent_name='Hephaestus',
        role='Developer',
        capabilities=['coding', 'debugging'],
        db_path='/tmp/agent_state.db'
    )
    dev_agent.start()

    time.sleep(2) # Give agents time to start

    dev_agent.request_task('Develop the user profile module')

    time.sleep(10) # Allow task to be processed and completed

    pm_agent.monitor_progress()

    # Stop agents
    pm_agent.stop()
    dev_agent.stop()
    logger.info("Project Manager Agent example finished.")

