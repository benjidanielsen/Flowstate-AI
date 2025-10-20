import json
import logging
import os
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import httpx
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.agents import SpecializedAgentOrchestrator
from .instrumentation import record_workflow_status, setup_observability, track_backend_call

try:
    from ai_gods.logging_config import setup_logging
except ModuleNotFoundError:  # pragma: no cover - fallback logger setup for tests
    def setup_logging(name: str, filename: str):
        logger = logging.getLogger(name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger
try:
    from evolution_framework.self_modification_orchestrator import SelfModificationOrchestrator
    from evolution_framework.evolution_governor import EvolutionGovernor
    from evolution_framework.evolution_manager import FlowstateEvolutionManager
    from evolution_framework.anomaly_detector import AnomalyDetector
    from evolution_framework.metrics_collector import MetricsCollector
except Exception:  # pragma: no cover - lightweight fallback for tests
    class MetricsCollector:  # type: ignore[override]
        def __init__(self, name: str):
            self.name = name

        def record_event(self, *_args: Any, **_kwargs: Any) -> None:
            logging.getLogger(self.name).debug("Metrics event skipped (fallback)")

    class FlowstateEvolutionManager:  # type: ignore[override]
        pass

    class AnomalyDetector:  # type: ignore[override]
        def __init__(self, *_args: Any, **_kwargs: Any):
            pass

    class EvolutionGovernor:  # type: ignore[override]
        def __init__(self, *_args: Any, **_kwargs: Any):
            pass

    class SelfModificationOrchestrator:  # type: ignore[override]
        def __init__(self, *_args: Any, **_kwargs: Any):
            pass

        def run_self_modification_cycle(self) -> None:
            logging.getLogger("self_mod").info("Self-modification cycle skipped (fallback)")
# Configuration
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3001")

app = FastAPI(title="Flowstate-AI Worker", version="1.0.0")
setup_observability(app)
# Initialize Evolution Framework components
metrics_collector = MetricsCollector("python_worker")
evolution_manager = FlowstateEvolutionManager()
anomaly_detector = AnomalyDetector(metrics_collector)
evolution_governor = EvolutionGovernor(evolution_manager, anomaly_detector, metrics_collector)
self_modification_orchestrator = SelfModificationOrchestrator(project_root="/home/ubuntu/Flowstate-AI", config_path=None)
specialized_orchestrator = SpecializedAgentOrchestrator()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Setup logging
logger = setup_logging(__name__, "python-worker.log")

class ReminderRequest(BaseModel):
    customer_id: str
    type: str
    message: str
    scheduled_for: datetime

class NBARequest(BaseModel):
    customer_id: Optional[str] = None
    limit: int = 10


class CustomerInsightsRequest(BaseModel):
    interaction: Dict[str, Any] = {}
    opportunities: List[Dict[str, Any]] = []
    integrations: List[Dict[str, Any]] = []
    metrics: Dict[str, float] = {}
    changes: Dict[str, float] = {}
    audience: Optional[str] = None

@app.get("/")
async def root():
    return {
        "message": "Flowstate-AI Python Worker",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "metricsEndpoint": "/metrics",
    }

@app.post("/reminders")
async def create_reminder(reminder: ReminderRequest):
    """Create a new reminder"""
    operation = "create_reminder"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{BACKEND_API_URL}/reminders",
                json={
                    "customer_id": reminder.customer_id,
                    "type": reminder.type,
                    "message": reminder.message,
                    "scheduled_for": reminder.scheduled_for.isoformat(),
                },
            )
            response.raise_for_status()
            result = response.json()
        return result
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while creating reminder", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        status = "error"
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)

@app.get("/reminders/due")
async def get_due_reminders():
    """Get all reminders that are due"""
    operation = "get_due_reminders"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_API_URL}/reminders/due")
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while fetching due reminders", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        status = "error"
        logger.error(f"Error fetching due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)

@app.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str):
    """Mark a reminder as complete"""
    operation = "complete_reminder"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/{reminder_id}/complete")
            response.raise_for_status()
            result = response.json()
            if not result:
                raise HTTPException(status_code=404, detail="Reminder not found")
            return result
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while completing reminder", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except HTTPException:
        status = "error"
        raise
    except Exception as e:
        status = "error"
        logger.error(f"Error completing reminder {reminder_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)

@app.post("/reminders/process-due")
async def process_due_reminders():
    """Process all due reminders and create follow-up actions"""
    operation = "process_due_reminders"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/process-due")
            response.raise_for_status()
            results = response.json()
        return {"processed": len(results), "results": results}
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while processing due reminders", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        status = "error"
        logger.error(f"Error processing due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)

@app.get("/nba")
async def get_next_best_actions(customer_id: Optional[str] = None, limit: int = 10):
    """Get Next Best Actions (NBA) recommendations"""
    operation = "get_nba"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            params = {"limit": limit}
            if customer_id:
                params["customer_id"] = customer_id
            response = await client.get(f"{BACKEND_API_URL}/nba", params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while fetching NBA recommendations", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        status = "error"
        logger.error(f"Error fetching NBA recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)

@app.post("/nba/analyze")
async def analyze_customer_data():
    """Analyze customer data and generate NBA recommendations"""
    operation = "analyze_nba"
    status = "success"
    start_time = time.perf_counter()
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/nba/analyze")
            response.raise_for_status()
            results = response.json()
        return {"analyzed": len(results), "recommendations": results}
    except httpx.HTTPStatusError as exc:
        status = "error"
        logger.error("Backend returned HTTP error while analyzing customer data", exc_info=exc)
        raise HTTPException(status_code=exc.response.status_code, detail=exc.response.text)
    except Exception as e:
        status = "error"
        logger.error(f"Error analyzing customer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        track_backend_call(operation, status, start_time)


@app.post("/agents/workflows/customer-insights")
async def run_customer_insights_workflow(request: CustomerInsightsRequest):
    """Execute the cross-agent customer insight workflow."""

    record_workflow_status("customer_insights", "started")
    try:
        result = await specialized_orchestrator.run_customer_insight_playbook(request.model_dump())
        record_workflow_status("customer_insights", "success")
        return result
    except Exception as exc:
        record_workflow_status("customer_insights", "error")
        logger.error("Failed to execute customer insights workflow", exc_info=exc)
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/autonomous-experimentation")
async def run_autonomous_experimentation():
    """Trigger a cycle of autonomous experimentation and self-modification."""
    try:
        record_workflow_status("autonomous_experimentation", "started")
        logger.info("Initiating autonomous experimentation cycle...")
        self_modification_orchestrator.run_self_modification_cycle()
        logger.info("Autonomous experimentation cycle completed.")
        record_workflow_status("autonomous_experimentation", "success")
        return {"status": "success", "message": "Autonomous experimentation cycle initiated."}
    except Exception as e:
        record_workflow_status("autonomous_experimentation", "error")
        logger.error(f"Error during autonomous experimentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PYTHON_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
