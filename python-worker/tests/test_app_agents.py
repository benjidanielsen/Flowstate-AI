import asyncio
import pytest

from app.agents import (
    InteractionAgent,
    IntegrationAgent,
    ReportingAgent,
    SalesIntelligenceAgent,
    SpecializedAgentOrchestrator,
)


@pytest.mark.asyncio
async def test_interaction_agent_generates_follow_up():
    agent = InteractionAgent()
    result = await agent.execute_task(
        "Call with prospect",
        {"transcript": "Great demo conversation", "sentimentScore": 0.6, "topics": ["demo", "pricing"]},
    )

    assert result["recommendedAction"].lower().startswith("schedule")
    assert result["sentiment"] == "positive"
    assert len(agent.local_memory) == 1


@pytest.mark.asyncio
async def test_sales_intelligence_agent_scores_pipeline():
    agent = SalesIntelligenceAgent()
    result = await agent.execute_task(
        "Score pipeline",
        {
            "opportunities": [
                {"id": 1, "name": "Acme", "fitScore": 75, "engagementScore": 82, "daysInStage": 14},
                {"id": 2, "name": "Globex", "fitScore": 40, "engagementScore": 30, "daysInStage": 60},
            ]
        },
    )

    assert result["averageScore"] > 0
    assert any(item["risk"] for item in result["insights"])


@pytest.mark.asyncio
async def test_reporting_agent_builds_summary():
    agent = ReportingAgent()
    result = await agent.execute_task(
        "Weekly summary",
        {"metrics": {"revenue": 120000, "conversion": 0.32}, "changes": {"revenue": 5000, "conversion": -0.01}},
    )

    assert "revenue" in result["summary"]
    assert len(result["highlights"]) == 2


@pytest.mark.asyncio
async def test_integration_agent_flags_incidents():
    agent = IntegrationAgent()
    result = await agent.execute_task(
        "Check integrations",
        {
            "integrations": [
                {"name": "CRM", "status": "ok", "latencyMs": 120, "lastSync": "2024-01-01T00:00:00Z"},
                {"name": "Billing", "status": "error", "latencyMs": 800, "lastSync": "2024-01-01T00:00:00Z"},
            ]
        },
    )

    assert result["requiresAttention"] is True
    assert len(result["incidents"]) == 1


@pytest.mark.asyncio
async def test_orchestrator_runs_cross_agent_playbook():
    orchestrator = SpecializedAgentOrchestrator()
    payload = {
        "interaction": {"transcript": "demo went great", "sentimentScore": 0.7, "topics": ["demo"]},
        "opportunities": [
            {"id": 1, "name": "Acme", "fitScore": 80, "engagementScore": 88, "daysInStage": 9},
        ],
        "integrations": [
            {"name": "CRM", "status": "ok", "latencyMs": 200, "lastSync": "2024-01-01T00:00:00Z"},
        ],
        "metrics": {"pipeline": 15},
        "changes": {"pipeline": 1},
    }

    result = await orchestrator.run_customer_insight_playbook(payload)

    assert set(result.keys()) == {"interaction", "pipeline", "integrations", "report"}
    assert result["interaction"]["recommendedAction"]
    assert result["pipeline"]["insights"]


@pytest.mark.asyncio
async def test_orchestrator_task_routing_validation():
    orchestrator = SpecializedAgentOrchestrator()

    with pytest.raises(ValueError):
        await orchestrator.route_task("unknown_agent", "", {})

    response = await orchestrator.route_task(
        "reporting_agent",
        "Assemble report",
        {"metrics": {"revenue": 1000}, "changes": {"revenue": 50}},
    )

    assert "summary" in response
