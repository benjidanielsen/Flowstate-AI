from __future__ import annotations

import os
import sys
from typing import Any, Dict
from unittest.mock import MagicMock

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.agents import CustomerAgent, PipelineAgent, ReminderAgent


def _mock_response(payload: Any) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    response.raise_for_status.return_value = None
    return response


def test_pipeline_stage_assignment_flow() -> None:
    session = MagicMock()
    session.get.return_value = _mock_response([
        {
            "id": "pipe-1",
            "name": "Frazer",
            "description": None,
            "stages": [
                {"id": "stage-1", "name": "Lead", "position": 0},
                {"id": "stage-2", "name": "Qualified", "position": 1},
            ],
        }
    ])
    session.post.return_value = _mock_response({"id": "cust-1", "pipeline_stage_id": "stage-2"})

    pipeline_agent = PipelineAgent(base_url="http://localhost/api", session=session)
    pipelines = pipeline_agent.list_pipelines()
    assert pipelines[0]["stages"][1]["name"] == "Qualified"

    customer = pipeline_agent.assign_customer_stage("cust-1", "stage-2")
    assert customer["pipeline_stage_id"] == "stage-2"


def test_customer_and_reminder_agents_share_session() -> None:
    session = MagicMock()

    def _dispatch(method: str, url: str, payload: Dict[str, Any]) -> MagicMock:
        response_payload = {"method": method, "url": url, **payload}
        return _mock_response(response_payload)

    session.get.side_effect = lambda url: _mock_response({"id": "cust-1", "name": "Test Customer"})
    session.put.side_effect = lambda url, json: _dispatch("PUT", url, json)
    session.post.side_effect = lambda url, json: _dispatch("POST", url, json)

    customer_agent = CustomerAgent(base_url="http://localhost/api", session=session)
    reminder_agent = ReminderAgent(base_url="http://localhost/api", session=session)

    customer = customer_agent.get_customer("cust-1")
    assert customer["name"] == "Test Customer"

    update_result = customer_agent.update_customer("cust-1", {"status": "Qualified"})
    assert update_result["status"] == "Qualified"
    assert update_result["method"] == "PUT"

    reminder_result = reminder_agent.create_reminder(
        "cust-1", {"message": "Follow up", "scheduled_for": "2024-01-01T10:00:00Z"}
    )
    assert reminder_result["method"] == "POST"
    assert "reminders" in reminder_result["url"]
