"""Reminder agent automates reminder scheduling workflows."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)


class ReminderAgent:
    """Automates reminder lifecycle management with the backend service."""

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:3001/api")
        self.session = session or requests.Session()
        LOGGER.debug("ReminderAgent initialized with base_url=%s", self.base_url)

    def list_by_customer(self, customer_id: str) -> List[Dict[str, Any]]:
        LOGGER.debug("Listing reminders for customer %s", customer_id)
        response = self.session.get(f"{self.base_url}/customers/{customer_id}/reminders")
        response.raise_for_status()
        return response.json()

    def create_reminder(self, customer_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        LOGGER.info("Creating reminder for customer %s", customer_id)
        response = self.session.post(f"{self.base_url}/customers/{customer_id}/reminders", json=payload)
        response.raise_for_status()
        return response.json()

    def mark_completed(self, reminder_id: str) -> Dict[str, Any]:
        LOGGER.info("Marking reminder %s as completed", reminder_id)
        response = self.session.put(f"{self.base_url}/reminders/{reminder_id}/complete")
        response.raise_for_status()
        return response.json()
