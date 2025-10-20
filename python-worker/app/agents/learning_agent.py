"""Learning agent responsible for synthesising analytics insights."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx

from .base import BaseAgent


@dataclass
class CustomerInsight:
    customer: Dict[str, Any]
    recent_events: List[Dict[str, Any]]
    last_event_at: Optional[datetime]
    high_intent_score: float
    risk_score: float
    summary: str


class LearningAgent(BaseAgent):
    """Derives structured insights from the analytics service."""

    def __init__(self, *, cache_ttl_seconds: int = 60) -> None:
        super().__init__()
        self._summary_cache: Optional[tuple[Dict[str, Any], datetime]] = None
        self._summary_ttl = timedelta(seconds=cache_ttl_seconds)

    async def fetch_summary(self, use_cache: bool = True) -> Optional[Dict[str, Any]]:
        if use_cache and self._summary_cache:
            summary, fetched_at = self._summary_cache
            if datetime.utcnow() - fetched_at < self._summary_ttl:
                return summary

        try:
            summary = await self._request("GET", "analytics/summary")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (403, 404):
                return None
            raise

        if summary is not None:
            self._summary_cache = (summary, datetime.utcnow())
        return summary

    async def get_recent_events(self, *, customer_id: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        params: Dict[str, Any] = {"limit": limit}
        if customer_id:
            params["customerId"] = customer_id

        try:
            events = await self._request("GET", "analytics/events", params=params)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code in (403, 404):
                return []
            raise

        return events or []

    async def build_customer_insight(self, customer_id: str) -> Optional[CustomerInsight]:
        try:
            customer = await self._request("GET", f"customers/{customer_id}")
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                return None
            raise

        recent_events = await self.get_recent_events(customer_id=customer_id)
        last_event_at = None
        if recent_events:
            raw_timestamp = recent_events[0].get("occurred_at") or recent_events[0].get("timestamp")
            if raw_timestamp:
                last_event_at = datetime.fromisoformat(str(raw_timestamp).replace("Z", "+00:00"))

        high_intent_score = self._score_high_intent(recent_events)
        risk_score = self._score_risk(customer, recent_events)
        summary = self._summarise(customer, recent_events, high_intent_score, risk_score)

        return CustomerInsight(
            customer=customer,
            recent_events=recent_events,
            last_event_at=last_event_at,
            high_intent_score=high_intent_score,
            risk_score=risk_score,
            summary=summary,
        )

    def _score_high_intent(self, events: List[Dict[str, Any]]) -> float:
        if not events:
            return 0.0
        weights = {
            "PURCHASED": 1.0,
            "MEETING_HELD": 0.8,
            "MEETING_BOOKED": 0.6,
            "LEAD_QUALIFIED": 0.5,
        }
        score = 0.0
        for event in events:
            score += weights.get(event.get("event_type") or event.get("eventType"), 0.1)
        return min(score, 1.5)

    def _score_risk(self, customer: Dict[str, Any], events: List[Dict[str, Any]]) -> float:
        risk = 0.2
        status = (customer.get("status") or "").lower()
        if "lost" in status or "inactive" in status:
            risk += 0.5
        if not events:
            risk += 0.3
        else:
            last_event = events[0]
            timestamp = last_event.get("occurred_at") or last_event.get("timestamp")
            if timestamp:
                try:
                    event_time = datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
                    days = (datetime.utcnow() - event_time).days
                    if days > 14:
                        risk += 0.2
                except ValueError:
                    risk += 0.1
        return min(risk, 1.0)

    def _summarise(
        self,
        customer: Dict[str, Any],
        events: List[Dict[str, Any]],
        intent: float,
        risk: float,
    ) -> str:
        pieces = [
            f"Customer {customer.get('name', customer.get('id', 'unknown'))}",
            f"intent score: {intent:.2f}",
            f"risk score: {risk:.2f}",
        ]
        if events:
            first_event = events[0]
            pieces.append(
                f"last event: {first_event.get('event_type') or first_event.get('eventType')}"
            )
        return " | ".join(pieces)
