"""Base utilities for specialized worker agents."""

from __future__ import annotations

import logging
import os
import time
from typing import Any, Dict, List, Optional

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3001")


class PrototypeAgent:
    """Base class for lightweight specialized agents used by the worker service."""

    def __init__(self, agent_name: str, capabilities: List[str]):
        self.agent_name = agent_name
        self.capabilities = capabilities
        self.backend_url = BACKEND_API_URL
        self.logger = logging.getLogger(f"agent.{agent_name}")
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
            self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)
        self.state: Dict[str, Any] = {"status": "active"}
        self._local_memory: List[Dict[str, Any]] = []

    @property
    def local_memory(self) -> List[Dict[str, Any]]:
        """Expose a copy of captured in-memory events for testing and orchestration."""

        return list(self._local_memory)

    async def register(self, initial_state: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        self.state = initial_state or {"status": "active", "capabilities": self.capabilities}
        return {"agentName": self.agent_name, "state": self.state}

    async def get_state(self) -> Dict[str, Any]:
        return self.state

    async def update_state(self, new_state: Dict[str, Any]) -> Dict[str, Any]:
        self.state.update(new_state)
        return self.state

    async def record_memory(
        self,
        *,
        content: str,
        memory_type: str = "general",
        tags: Optional[List[str]] = None,
        importance: int = 5,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Record a memory locally and optionally synchronize with the backend."""

        entry = {
            "content": content,
            "type": memory_type,
            "tags": tags or [],
            "importance": importance,
            "metadata": metadata or {},
            "timestamp": time.time(),
        }
        self._local_memory.append(entry)

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:  # pragma: no cover - interface
        raise NotImplementedError("Prototype agents must implement execute_task")
