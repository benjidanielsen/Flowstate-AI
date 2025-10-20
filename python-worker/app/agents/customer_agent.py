"""Customer agent coordinates customer lifecycle management."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import requests

LOGGER = logging.getLogger(__name__)


class CustomerAgent:
    """Wraps customer-centric operations offered by the backend."""

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:3001/api")
        self.session = session or requests.Session()
        LOGGER.debug("CustomerAgent initialized with base_url=%s", self.base_url)

    def get_customer(self, customer_id: str) -> Dict[str, Any]:
        LOGGER.debug("Fetching customer %s", customer_id)
        response = self.session.get(f"{self.base_url}/customers/{customer_id}")
        response.raise_for_status()
        return response.json()

    def update_customer(self, customer_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        LOGGER.info("Updating customer %s", customer_id)
        response = self.session.put(f"{self.base_url}/customers/{customer_id}", json=payload)
        response.raise_for_status()
        return response.json()

    def record_interaction(self, customer_id: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        LOGGER.info("Recording interaction for customer %s", customer_id)
        response = self.session.post(f"{self.base_url}/customers/{customer_id}/interactions", json=payload)
        response.raise_for_status()
        return response.json()
