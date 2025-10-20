"""Base classes and utilities for worker agents."""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import httpx


class BaseAgent:
    """Shared helpers for agents interacting with the Flowstate backend."""

    def __init__(self, *, base_url: Optional[str] = None, timeout: float = 15.0) -> None:
        self.base_url = base_url or os.getenv("BACKEND_API_URL", "http://localhost:3001/api")
        self.timeout = timeout
        self._default_headers: Dict[str, str] = {"Content-Type": "application/json"}
        token = os.getenv("BACKEND_SERVICE_TOKEN")
        if token:
            self._default_headers["Authorization"] = f"Bearer {token}"
        self._feature_flag_cache: Dict[str, tuple[bool, datetime]] = {}
        cache_ttl = int(os.getenv("FEATURE_FLAG_CACHE_TTL", "45"))
        self._feature_flag_ttl = timedelta(seconds=cache_ttl)

    def _build_url(self, path: str) -> str:
        return f"{self.base_url.rstrip('/')}/{path.lstrip('/')}"

    async def _request(
        self,
        method: str,
        path: str,
        *,
        json: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Any:
        url = self._build_url(path)
        merged_headers = dict(self._default_headers)
        if headers:
            merged_headers.update({k: v for k, v in headers.items() if v is not None})

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.request(method, url, json=json, params=params, headers=merged_headers)
            response.raise_for_status()
            if not response.content:
                return None
            try:
                return response.json()
            except ValueError:
                return response.text

    async def is_feature_enabled(self, flag_key: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """Evaluate whether a feature flag is enabled for the provided context."""

        context = {k: v for k, v in (context or {}).items() if v}
        cache_key = self._build_cache_key(flag_key, context)
        cached = self._feature_flag_cache.get(cache_key)
        if cached:
            enabled, fetched_at = cached
            if datetime.utcnow() - fetched_at < self._feature_flag_ttl:
                return enabled

        try:
            payload = await self._request("GET", f"feature-flags/{flag_key}", params=context or None)
            enabled = bool(payload and payload.get("enabledForContext"))
        except httpx.HTTPStatusError as exc:  # pragma: no cover - network failure path
            if exc.response.status_code == 404:
                enabled = False
            else:
                raise

        self._feature_flag_cache[cache_key] = (enabled, datetime.utcnow())
        return enabled

    def _build_cache_key(self, flag_key: str, context: Dict[str, Any]) -> str:
        if not context:
            return flag_key
        ctx = ",".join(f"{key}={context[key]}" for key in sorted(context))
        return f"{flag_key}:{ctx}"

    async def record_recommendations(self, entries: list[Dict[str, Any]]) -> None:
        if not entries:
            return
        for entry in entries:
            await self._request("POST", "analytics/recommendations", json=entry)

    async def post_analytics(self, payload: Dict[str, Any]) -> None:
        await self._request("POST", "analytics/events", json=payload)

    async def gather_with_concurrency(self, limit: int, *aws: Any) -> list[Any]:
        semaphore = asyncio.Semaphore(limit)

        async def sem_task(aw):
            async with semaphore:
                return await aw

        return await asyncio.gather(*(sem_task(aw) for aw in aws))
