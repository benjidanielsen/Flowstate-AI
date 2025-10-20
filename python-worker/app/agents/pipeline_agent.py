"""Pipeline agent orchestrates pipeline and stage management using the backend API."""
from __future__ import annotations

import logging
import os
from typing import Any, Dict, List, Optional

import requests

LOGGER = logging.getLogger(__name__)


class PipelineAgent:
    """Provides a high-level helper to manage pipelines via the backend REST API."""

    def __init__(self, base_url: Optional[str] = None, session: Optional[requests.Session] = None) -> None:
        self.base_url = base_url or os.getenv("BACKEND_URL", "http://localhost:3001/api")
        self.session = session or requests.Session()
        LOGGER.debug("PipelineAgent initialized with base_url=%s", self.base_url)

    # ---- Pipeline operations -------------------------------------------------
    def list_pipelines(self) -> List[Dict[str, Any]]:
        LOGGER.debug("Fetching pipelines from %s", self.base_url)
        response = self.session.get(f"{self.base_url}/pipelines")
        response.raise_for_status()
        return response.json()

    def get_pipeline(self, pipeline_id: str) -> Dict[str, Any]:
        LOGGER.debug("Fetching pipeline %s", pipeline_id)
        response = self.session.get(f"{self.base_url}/pipelines/{pipeline_id}")
        response.raise_for_status()
        return response.json()

    def create_pipeline(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        LOGGER.info("Creating pipeline %s", payload.get("name"))
        response = self.session.post(f"{self.base_url}/pipelines", json=payload)
        response.raise_for_status()
        return response.json()

    # ---- Stage operations ----------------------------------------------------
    def upsert_stage(self, pipeline_id: str, stage_payload: Dict[str, Any], stage_id: Optional[str] = None) -> Dict[str, Any]:
        LOGGER.info("Upserting stage %s for pipeline %s", stage_payload.get("name"), pipeline_id)
        endpoint = f"{self.base_url}/pipelines/{pipeline_id}/stages"
        if stage_id:
            endpoint = f"{endpoint}/{stage_id}"
            response = self.session.put(endpoint, json=stage_payload)
        else:
            response = self.session.post(endpoint, json=stage_payload)
        response.raise_for_status()
        return response.json()

    def assign_customer_stage(self, customer_id: str, stage_id: str) -> Dict[str, Any]:
        LOGGER.info("Assigning customer %s to stage %s", customer_id, stage_id)
        response = self.session.post(
            f"{self.base_url}/pipelines/customers/{customer_id}/stage",
            json={"stageId": stage_id},
        )
        response.raise_for_status()
        return response.json()
