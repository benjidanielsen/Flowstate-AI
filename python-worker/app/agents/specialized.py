"""Prototype specialized agents used by the worker orchestration layer."""

from __future__ import annotations

"""Prototype specialized agents used by the worker orchestration layer."""

from statistics import mean
from typing import Any, Dict, List

from .base import PrototypeAgent


class InteractionAgent(PrototypeAgent):
    """Analyzes customer conversations and surfaces follow-up actions."""

    def __init__(self) -> None:
        super().__init__(
            agent_name="interaction_agent",
            capabilities=["interaction_analysis", "sentiment_tracking", "next_steps"],
        )

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        transcript: str = context.get("transcript", "")
        sentiment_score = context.get("sentimentScore", 0.0)
        topics: List[str] = context.get("topics", [])

        await self.record_memory(
            content=f"Analyzed interaction: {task_description[:80]}",
            memory_type="interaction",
            tags=["interaction", "analysis"],
            importance=6,
            metadata={"sentiment": sentiment_score, "topics": topics},
        )

        follow_up = "Schedule demo" if "demo" in transcript.lower() else "Send recap email"
        sentiment_label = "positive" if sentiment_score >= 0.25 else "neutral" if sentiment_score > -0.25 else "negative"

        return {
            "agent": self.agent_name,
            "summary": transcript[:120],
            "sentiment": sentiment_label,
            "topics": topics,
            "recommendedAction": follow_up,
        }


class SalesIntelligenceAgent(PrototypeAgent):
    """Scores pipeline opportunities and highlights risks."""

    def __init__(self) -> None:
        super().__init__(
            agent_name="sales_intelligence_agent",
            capabilities=["pipeline_scoring", "deal_risk", "insights"],
        )

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        opportunities: List[Dict[str, Any]] = context.get("opportunities", [])
        if not opportunities:
            return {
                "agent": self.agent_name,
                "insights": [],
                "averageScore": 0,
                "message": "No opportunities provided",
            }

        enriched = []
        for opp in opportunities:
            score_components = [
                float(opp.get("fitScore", 0)),
                float(opp.get("engagementScore", 0)),
                100 - float(opp.get("daysInStage", 0)),
            ]
            normalized = max(min(mean(score_components) / 100, 1.0), 0.0)
            risk_reason = "Low engagement" if opp.get("engagementScore", 0) < 40 else "Long stage duration"
            enriched.append(
                {
                    "id": opp.get("id"),
                    "name": opp.get("name"),
                    "score": round(normalized, 2),
                    "nextStep": opp.get("nextStep", "Define next action"),
                    "risk": risk_reason if normalized < 0.5 else None,
                }
            )

        await self.record_memory(
            content=f"Scored {len(enriched)} opportunities",
            memory_type="sales",
            tags=["pipeline", "scoring"],
            importance=5,
        )

        return {
            "agent": self.agent_name,
            "insights": enriched,
            "averageScore": round(mean([item["score"] for item in enriched]), 2),
        }


class ReportingAgent(PrototypeAgent):
    """Builds digestible summaries for leadership and account teams."""

    def __init__(self) -> None:
        super().__init__(
            agent_name="reporting_agent",
            capabilities=["report_generation", "trend_analysis", "kpi_tracking"],
        )

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        metrics: Dict[str, float] = context.get("metrics", {})
        changes: Dict[str, float] = context.get("changes", {})

        highlights = []
        for metric, value in metrics.items():
            delta = changes.get(metric, 0.0)
            direction = "up" if delta > 0 else "down" if delta < 0 else "flat"
            highlights.append(
                {
                    "metric": metric,
                    "value": value,
                    "change": delta,
                    "direction": direction,
                }
            )

        await self.record_memory(
            content=f"Generated report with {len(highlights)} highlights",
            memory_type="report",
            tags=["report", "kpi"],
            importance=4,
        )

        summary_lines = [
            f"{item['metric']}: {item['value']} ({item['direction']} {item['change']})" for item in highlights
        ]

        return {
            "agent": self.agent_name,
            "highlights": highlights,
            "summary": "; ".join(summary_lines),
            "audience": context.get("audience", "leadership"),
        }


class IntegrationAgent(PrototypeAgent):
    """Monitors and coordinates external system integrations."""

    def __init__(self) -> None:
        super().__init__(
            agent_name="integration_agent",
            capabilities=["integration_health", "sync_management", "alerting"],
        )

    async def execute_task(self, task_description: str, context: Dict[str, Any]) -> Dict[str, Any]:
        integrations: List[Dict[str, Any]] = context.get("integrations", [])
        results: List[Dict[str, Any]] = []

        for integration in integrations:
            status = integration.get("status", "unknown")
            latency = float(integration.get("latencyMs", 0))
            status_label = "healthy" if status == "ok" and latency < 500 else "degraded"
            results.append(
                {
                    "name": integration.get("name"),
                    "status": status_label,
                    "latencyMs": latency,
                    "lastSync": integration.get("lastSync"),
                }
            )

        await self.record_memory(
            content=f"Evaluated {len(results)} integrations",
            memory_type="integration",
            tags=["integration", "health"],
            importance=5,
        )

        incidents = [item for item in results if item["status"] != "healthy"]

        return {
            "agent": self.agent_name,
            "integrations": results,
            "incidents": incidents,
            "requiresAttention": len(incidents) > 0,
        }


__all__ = [
    "InteractionAgent",
    "SalesIntelligenceAgent",
    "ReportingAgent",
    "IntegrationAgent",
]
