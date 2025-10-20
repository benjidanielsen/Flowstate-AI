"""NBA agent that leverages vector search to prioritise actions."""

from __future__ import annotations

import math
import os
from typing import Any, Dict, List, Optional
from uuid import uuid4

import httpx

from .base import BaseAgent
from .learning_agent import CustomerInsight, LearningAgent


class VectorSearchNBAAgent(BaseAgent):
    """Generates Next Best Action recommendations using semantic context."""

    def __init__(self, learning_agent: Optional[LearningAgent] = None) -> None:
        super().__init__()
        self.learning_agent = learning_agent or LearningAgent()
        self.agent_name = os.getenv("NBA_AGENT_NAME", "vector_nba_agent")

    async def generate_prioritized_recommendations(
        self,
        *,
        customer_id: Optional[str] = None,
        limit: int = 5,
    ) -> List[Dict[str, Any]]:
        rollout_context = {"fallbackId": customer_id or self.agent_name}
        vector_enabled = await self.is_feature_enabled("nba_vector_recommendations", rollout_context)
        if not vector_enabled:
            return await self._generate_fallback(customer_id=customer_id, limit=limit)

        if customer_id:
            insight = await self.learning_agent.build_customer_insight(customer_id)
            if not insight:
                return []
            query = self._build_customer_query(insight)
            vector_results = await self._semantic_search(query, limit=limit + 2)
            recommendations = self._hydrate_customer_recommendations(insight, vector_results, limit)
        else:
            summary = await self.learning_agent.fetch_summary()
            if not summary:
                return await self._generate_fallback(customer_id=None, limit=limit)
            query = self._build_org_query(summary)
            vector_results = await self._semantic_search(query, limit=limit + 3)
            recommendations = self._hydrate_global_recommendations(summary, vector_results, limit)

        logging_enabled = await self.is_feature_enabled(
            "analytics_recommendation_logging",
            {"fallbackId": self.agent_name},
        )
        if logging_enabled and recommendations:
            await self.record_recommendations(
                [
                    {
                        "recommendationId": rec["id"],
                        "agentName": self.agent_name,
                        "customerId": rec.get("customer_id"),
                        "recommendationType": rec.get("action_type"),
                        "priority": rec.get("priority"),
                        "score": rec.get("score"),
                        "context": rec.get("context"),
                        "metadata": {"reasoning": rec.get("reasoning")},
                    }
                    for rec in recommendations
                ]
            )

        return recommendations[:limit]

    async def _semantic_search(self, query: str, *, limit: int = 5, threshold: float = 0.55) -> List[Dict[str, Any]]:
        payload = {"query": query, "limit": limit, "threshold": threshold}
        try:
            response = await self._request("POST", "search/semantic", json=payload)
        except httpx.HTTPStatusError as exc:
            if exc.response.status_code == 404:
                response = await self._request("POST", "api/search/semantic", json=payload)
            else:
                raise

        if isinstance(response, dict):
            return response.get("results", [])
        return response or []

    def _build_customer_query(self, insight: CustomerInsight) -> str:
        parts = [insight.summary]
        for event in insight.recent_events[:5]:
            event_type = event.get("event_type") or event.get("eventType")
            if event_type:
                parts.append(f"event:{event_type}")
        return "\n".join(parts)

    def _build_org_query(self, summary: Dict[str, Any]) -> str:
        pipeline = summary.get("pipeline", {})
        status_parts = [f"{item['status']}:{item['count']}" for item in pipeline.get("byStatus", [])]
        top_events = [
            f"{item['eventType']}:{item['count']}" for item in summary.get("events", {}).get("byType", [])[:5]
        ]
        return "\n".join(["overall pipeline health"] + status_parts + top_events)

    def _hydrate_customer_recommendations(
        self,
        insight: CustomerInsight,
        results: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []
        for index, result in enumerate(results[: limit * 2]):
            similarity = float(result.get("similarity") or 0.0)
            priority = self._calculate_priority(similarity, insight.high_intent_score, insight.risk_score)
            recommendation_id = f"{uuid4()}"
            recommendations.append(
                {
                    "id": recommendation_id,
                    "customer_id": insight.customer.get("id"),
                    "action_type": result.get("metadata", {}).get("action") or "vector_follow_up",
                    "title": result.get("metadata", {}).get("title") or "Follow up with personalised insight",
                    "description": result.get("content")[:240] if result.get("content") else "Review recommended action.",
                    "priority": priority,
                    "urgency": self._priority_to_urgency(priority),
                    "score": similarity,
                    "pipeline_status": insight.customer.get("status"),
                    "reasoning": insight.summary,
                    "context": {
                        "vector_document_id": result.get("id"),
                        "similarity": similarity,
                        "last_event_at": insight.last_event_at.isoformat() if insight.last_event_at else None,
                    },
                }
            )
        return recommendations[:limit]

    def _hydrate_global_recommendations(
        self,
        summary: Dict[str, Any],
        results: List[Dict[str, Any]],
        limit: int,
    ) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []
        dominant_status = max(
            summary.get("pipeline", {}).get("byStatus", []),
            key=lambda item: item.get("count", 0),
            default={"status": "Pipeline"},
        ).get("status", "Pipeline")

        for index, result in enumerate(results[: limit * 2]):
            similarity = float(result.get("similarity") or 0.0)
            priority = min(100, int(similarity * 100) + 30)
            recommendations.append(
                {
                    "id": str(uuid4()),
                    "customer_id": None,
                    "action_type": result.get("metadata", {}).get("action") or "pipeline_optimisation",
                    "title": result.get("metadata", {}).get("title") or f"Optimise {dominant_status} stage",
                    "description": result.get("content")[:200] if result.get("content") else "Review strategic insight.",
                    "priority": priority,
                    "urgency": self._priority_to_urgency(priority),
                    "score": similarity,
                    "pipeline_status": dominant_status,
                    "reasoning": "Organisation-wide prioritisation derived from analytics summary.",
                    "context": {
                        "vector_document_id": result.get("id"),
                        "similarity": similarity,
                    },
                }
            )
        return recommendations[:limit]

    async def _generate_fallback(self, *, customer_id: Optional[str], limit: int) -> List[Dict[str, Any]]:
        recommendations: List[Dict[str, Any]] = []
        if customer_id:
            insight = await self.learning_agent.build_customer_insight(customer_id)
            if not insight:
                return []
            base_priority = max(60, int(insight.high_intent_score * 80))
            recommendations.append(
                {
                    "id": str(uuid4()),
                    "customer_id": customer_id,
                    "action_type": "manual_follow_up",
                    "title": "Review customer timeline",
                    "description": insight.summary,
                    "priority": base_priority,
                    "urgency": self._priority_to_urgency(base_priority),
                    "score": insight.high_intent_score,
                    "pipeline_status": insight.customer.get("status"),
                    "reasoning": "Fallback heuristic recommendation.",
                    "context": {},
                }
            )
        else:
            summary = await self.learning_agent.fetch_summary(use_cache=False)
            total_events = summary.get("events", {}).get("total", 0) if summary else 0
            priority = 70 if total_events else 40
            recommendations.append(
                {
                    "id": str(uuid4()),
                    "customer_id": None,
                    "action_type": "review_pipeline",
                    "title": "Review pipeline conversion metrics",
                    "description": "Vector rollout disabled; falling back to KPI review.",
                    "priority": priority,
                    "urgency": self._priority_to_urgency(priority),
                    "score": 0.0,
                    "pipeline_status": "Pipeline",
                    "reasoning": "Fallback global recommendation due to feature flag.",
                    "context": {"total_events": total_events},
                }
            )
        return recommendations[:limit]

    def _calculate_priority(self, similarity: float, intent_score: float, risk_score: float) -> int:
        base = similarity * 70 + intent_score * 25 - risk_score * 20
        return max(10, min(100, int(math.ceil(base))))

    def _priority_to_urgency(self, priority: int) -> str:
        if priority >= 80:
            return "high"
        if priority >= 60:
            return "medium"
        return "low"
