#!/usr/bin/env python3
"""
VSCode Agent Integration Module
Connects the existing AI agents with the VSCode backend API
"""

import asyncio
import json
import logging
import requests
import redis
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class VSCodeAgentIntegration:
    """
    Integration layer between AI agents and VSCode extension
    """
    
    def __init__(self, backend_url: str = 'http://localhost:3001'):
        self.backend_url = backend_url
        self.agent_id = None
        
        # Initialize Redis for real-time communication
        try:
            self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
            self.redis_client.ping()
            self.pubsub = self.redis_client.pubsub()
            logger.info("✅ Connected to Redis")
        except Exception as e:
            logger.warning(f"⚠️ Redis not available: {e}")
            self.redis_client = None
            self.pubsub = None
    
    def register_agent(self, agent_id: str, initial_status: str = 'IDLE'):
        """Register an agent with the VSCode backend"""
        self.agent_id = agent_id
        
        try:
            response = requests.post(
                f'{self.backend_url}/api/agents/status/{agent_id}',
                json={
                    'status': initial_status,
                    'current_task': '',
                    'progress': 0
                },
                timeout=5
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Agent {agent_id} registered with VSCode backend")
                return True
            else:
                logger.error(f"❌ Failed to register agent: {response.text}")
                return False
        except Exception as e:
            logger.error(f"❌ Error registering agent: {e}")
            return False
    
    def update_status(self, status: str, current_task: str = '', progress: int = 0):
        """Update agent status in the VSCode backend"""
        if not self.agent_id:
            logger.warning("Agent not registered. Call register_agent() first.")
            return False
        
        try:
            response = requests.post(
                f'{self.backend_url}/api/agents/status/{self.agent_id}',
                json={
                    'status': status,
                    'current_task': current_task,
                    'progress': progress
                },
                timeout=5
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating status: {e}")
            return False
    
    def create_task(self, name: str, description: str = '', assigned_to: str = '') -> Optional[int]:
        """Create a new task in the VSCode backend"""
        try:
            response = requests.post(
                f'{self.backend_url}/api/tasks',
                json={
                    'name': name,
                    'description': description,
                    'assigned_to': assigned_to
                },
                timeout=5
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('task_id')
            else:
                logger.error(f"Failed to create task: {response.text}")
                return None
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            return None
    
    def update_task(self, task_id: int, status: str, assigned_to: Optional[str] = None):
        """Update a task in the VSCode backend"""
        try:
            payload = {'status': status}
            if assigned_to:
                payload['assigned_to'] = assigned_to
            
            response = requests.put(
                f'{self.backend_url}/api/tasks/{task_id}',
                json=payload,
                timeout=5
            )
            
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            return False
    
    def listen_for_commands(self, callback):
        """Listen for commands from VSCode extension via Redis"""
        if not self.pubsub:
            logger.warning("Redis not available. Cannot listen for commands.")
            return
        
        self.pubsub.subscribe('system_command')
        logger.info("👂 Listening for VSCode commands...")
        
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                try:
                    data = json.loads(message['data'])
                    command = data.get('command')
                    
                    logger.info(f"📨 Received command: {command}")
                    callback(command, data)
                except Exception as e:
                    logger.error(f"Error processing command: {e}")
    
    def send_code_manipulation_request(self, action: str, file: str, **kwargs):
        """Send a code manipulation request to VSCode extension"""
        if not self.redis_client:
            logger.warning("Redis not available. Cannot send code manipulation request.")
            return False
        
        try:
            payload = {
                'action': action,
                'file': file,
                **kwargs
            }
            
            self.redis_client.publish('code_manipulation', json.dumps(payload))
            logger.info(f"📤 Sent code manipulation request: {action} {file}")
            return True
        except Exception as e:
            logger.error(f"Error sending code manipulation request: {e}")
            return False
    
    def send_terminal_command(self, command: str, terminal_name: str = 'FlowState-AI'):
        """Send a terminal command to VSCode extension"""
        if not self.redis_client:
            logger.warning("Redis not available. Cannot send terminal command.")
            return False
        
        try:
            payload = {
                'command': command,
                'terminalName': terminal_name
            }
            
            self.redis_client.publish('terminal_command', json.dumps(payload))
            logger.info(f"📤 Sent terminal command: {command}")
            return True
        except Exception as e:
            logger.error(f"Error sending terminal command: {e}")
            return False
    
    def notify_vscode(self, message: str, level: str = 'info'):
        """Send a notification to VSCode"""
        if not self.redis_client:
            return False
        
        try:
            payload = {
                'message': message,
                'level': level,
                'timestamp': datetime.now().isoformat()
            }
            
            self.redis_client.publish('vscode_notification', json.dumps(payload))
            return True
        except Exception as e:
            logger.error(f"Error sending notification: {e}")
            return False

# Example usage
if __name__ == '__main__':
    # Initialize integration
    integration = VSCodeAgentIntegration()
    
    # Register as Project Manager AI
    integration.register_agent('project-manager-ai', 'ACTIVE')
    
    # Update status
    integration.update_status('ACTIVE', 'Orchestrating development tasks', 25)
    
    # Create a task
    task_id = integration.create_task(
        'Implement user authentication',
        'Add JWT-based authentication to the API',
        'backend-agent'
    )
    
    if task_id:
        logger.info(f"Created task with ID: {task_id}")
        
        # Update task status
        integration.update_task(task_id, 'IN_PROGRESS', 'backend-agent')
    
    # Send a code manipulation request
    integration.send_code_manipulation_request(
        'create',
        'src/auth/jwt.ts',
        content='// JWT authentication module\n\nexport function generateToken() {\n  // TODO: Implement\n}\n'
    )
    
    # Send a terminal command
    integration.send_terminal_command('npm install jsonwebtoken')
    
    # Send a notification
    integration.notify_vscode('✅ Authentication module scaffolded successfully', 'info')
    
    logger.info("✅ VSCode integration demo completed")
