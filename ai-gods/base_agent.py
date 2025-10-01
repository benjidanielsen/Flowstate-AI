#!/usr/bin/env python3
"""
🤖 BASE AGENT - The Foundation for all AI Agents
"""

import requests
import random
import string
import os
from datetime import datetime
import logging
from typing import Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('BaseAgent')

GODMODE_DASHBOARD_URL = os.getenv('GODMODE_DASHBOARD_URL', 'http://localhost:3333/api/update_agent_status')

class BaseAgent:
    def __init__(self, agent_name, agent_type):
        self.agent_name = agent_name
        self.agent_type = agent_type
        self.agent_human_name = self.generate_human_name()
        self.gender = self.get_gender()
        self.profile_picture = self.get_profile_picture()
        self.status = "Idle"
        self.current_task = "None"
        self.progress = 0

    def generate_human_name(self):
        # Generate a random human-like name
        first_names = ["Alex", "Jordan", "Taylor", "Morgan", "Casey"]
        last_names = ["Smith", "Jones", "Williams", "Brown", "Davis"]
        return f"{random.choice(first_names)} {random.choice(last_names)}"

    def get_gender(self):
        # Determine gender based on the first name
        return "male" if self.agent_human_name.split()[0] in ["Alex", "Jordan", "Casey"] else "female"

    def get_profile_picture(self):
        # Use a default placeholder for the profile picture
        return f"/static/profile_pictures/{self.gender}_placeholder.jpg"

    def update_status(self, status, current_task, progress):
        self.status = status
        self.current_task = current_task
        self.progress = progress
        self.report_status()

    def report_status(self):
        # Report status to the dashboard
        try:
            requests.post("http://127.0.0.1:3333/api/update_agent_status", json={
                "agent_name": self.agent_name,
                "agent_human_name": self.agent_human_name,
                "gender": self.gender,
                "profile_picture": self.profile_picture,
                "status": self.status,
                "current_task": self.current_task,
                "progress": self.progress
            })
        except requests.exceptions.RequestException as e:
            print(f"Error reporting status: {e}")



    def send_message_to_hub(self, receiver: str, message_type: str, content: Any):
        """Sends a message to the AI Communication Hub for routing to another agent."""
        try:
            payload = {
                "sender": self.agent_name,
                "receiver": receiver,
                "type": message_type,
                "content": content,
                "timestamp": datetime.now().isoformat()
            }
            # Assuming the Communication Hub has an API endpoint to receive messages
            # This would typically be an internal API call or a direct method invocation if running in the same process
            # For now, we'll log it and simulate an API call if a dashboard URL is available.
            if GODMODE_DASHBOARD_URL:
                logger.info(f"✉️ {self.agent_human_name} sending message to {receiver} via Hub: Type={message_type}, Content={content}")
                # Send a POST request to the Communication Hub's message endpoint
                communication_hub_url = GODMODE_DASHBOARD_URL.replace('/api/update_agent_status', '/api/message')
                requests.post(communication_hub_url, json=payload)
                
                # Also send to the dashboard for admin visibility
                dashboard_message_url = GODMODE_DASHBOARD_URL.replace('/api/update_agent_status', '/api/agent_message')
                requests.post(dashboard_message_url, json=payload)
            else:
                logger.warning(f"✉️ {self.agent_human_name} cannot send message to {receiver} via Hub: GODMODE_DASHBOARD_URL not set.")
        except Exception as e:
            logger.error(f"Error sending message to Communication Hub: {e}")



    def request_cross_check(self, target_agent: str, item_to_check: str, context: str):
        """Requests another agent to cross-check a piece of information or a task."""
        message_content = {
            "action": "cross_check_request",
            "item": item_to_check,
            "context": context
        }
        self.send_message_to_hub(target_agent, "cross_check", message_content)
        logger.info(f"🔍 {self.agent_human_name} requested cross-check from {target_agent} on: {item_to_check}")

    def report_anomaly(self, anomalous_agent: str, anomaly_description: str, severity: str = "medium"):
        """Reports an anomaly or unusual behavior of another agent to the Communication Hub."""
        message_content = {
            "action": "anomaly_report",
            "anomalous_agent": anomalous_agent,
            "description": anomaly_description,
            "severity": severity
        }
        # Send to the Communication Hub, which can then route to a dedicated Oversight AI if one exists
        self.send_message_to_hub("ai-communication-hub", "anomaly_report", message_content)
        logger.warning(f"🚨 {self.agent_human_name} reported anomaly for {anomalous_agent}: {anomaly_description} (Severity: {severity})")

