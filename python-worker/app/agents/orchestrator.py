"""Orchestration utilities for coordinating prototype specialized agents."""

from __future__ import annotations

from typing import Any, Dict, Iterable, List

from .specialized import (
    InteractionAgent,
    IntegrationAgent,
    ReportingAgent,
    SalesIntelligenceAgent,
)

AgentMap = Dict[str, Any]


class SpecializedAgentOrchestrator:
    """Coordinates specialized worker agents for multi-step workflows."""

    def __init__(self, agents: Iterable[Any] | None = None) -> None:
        self.agents: AgentMap = {agent.agent_name: agent for agent in (agents or self._build_default_agents())}

    @staticmethod
    def _build_default_agents() -> List[Any]:
        return [
            InteractionAgent(),
            SalesIntelligenceAgent(),
            ReportingAgent(),
            IntegrationAgent(),
        ]

    async def ensure_registered(self) -> Dict[str, Dict[str, Any]]:
        """Register all agents with the backend (if available)."""

        registration_results: Dict[str, Dict[str, Any]] = {}
        for agent in self.agents.values():
            try:
                registration_results[agent.agent_name] = await agent.register()
            except Exception as exc:  # pragma: no cover - best effort registration
                agent.logger.warning("Agent registration failed", exc_info=exc)
                registration_results[agent.agent_name] = {"status": "failed", "error": str(exc)}
        return registration_results

    async def route_task(self, agent_name: str, description: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if agent_name not in self.agents:
            raise ValueError(f"Agent '{agent_name}' is not registered with the orchestrator")
        agent = self.agents[agent_name]
        return await agent.execute_task(description, payload)

    async def run_customer_insight_playbook(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Coordinate a cross-agent workflow that surfaces actionable insights."""

        interaction_result = await self.agents["interaction_agent"].execute_task(
            "Analyze latest customer touchpoint",
            payload.get("interaction", {}),
        )

        pipeline_result = await self.agents["sales_intelligence_agent"].execute_task(
            "Score deals impacted by touchpoint",
            {"opportunities": payload.get("opportunities", [])},
        )

        integration_result = await self.agents["integration_agent"].execute_task(
            "Check supporting integrations",
            {"integrations": payload.get("integrations", [])},
        )

        report_payload = {
            "metrics": payload.get("metrics", {}),
            "changes": payload.get("changes", {}),
            "audience": payload.get("audience", "executive"),
        }
        reporting_result = await self.agents["reporting_agent"].execute_task(
            "Synthesize leadership briefing",
            report_payload,
        )

        return {
            "interaction": interaction_result,
            "pipeline": pipeline_result,
            "integrations": integration_result,
            "report": reporting_result,
        }


__all__ = ["SpecializedAgentOrchestrator"]
