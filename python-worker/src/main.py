import json
import logging
import os
import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3001")
from ai_gods.logging_config import setup_logging
from evolution_framework.self_modification_orchestrator import SelfModificationOrchestrator
from evolution_framework.evolution_governor import EvolutionGovernor
from evolution_framework.evolution_manager import FlowstateEvolutionManager
from evolution_framework.anomaly_detector import AnomalyDetector
from evolution_framework.metrics_collector import MetricsCollector
app = FastAPI(title="Flowstate-AI Worker", version="1.0.0")
# Initialize Evolution Framework components
metrics_collector = MetricsCollector("python_worker")
evolution_manager = FlowstateEvolutionManager()
anomaly_detector = AnomalyDetector(metrics_collector)
evolution_governor = EvolutionGovernor(evolution_manager, anomaly_detector, metrics_collector)
self_modification_orchestrator = SelfModificationOrchestrator(project_root="/home/ubuntu/Flowstate-AI", config_path=None)

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

@app.get("/")
async def root():
    return {
        "message": "Flowstate-AI Python Worker",
        "timestamp": datetime.now().isoformat(),
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.post("/reminders")
async def create_reminder(reminder: ReminderRequest):
    """Create a new reminder"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders", json={
                "customer_id": reminder.customer_id,
                "type": reminder.type,
                "message": reminder.message,
                "scheduled_for": reminder.scheduled_for.isoformat()
            })
            response.raise_for_status()
            result = response.json()
        return result
    except Exception as e:
        logger.error(f"Error creating reminder: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reminders/due")
async def get_due_reminders():
    """Get all reminders that are due"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BACKEND_API_URL}/reminders/due")
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str):
    """Mark a reminder as complete"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/{reminder_id}/complete")
            response.raise_for_status()
            result = response.json()
            if not result:
                raise HTTPException(status_code=404, detail="Reminder not found")
            return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing reminder {reminder_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/process-due")
async def process_due_reminders():
    """Process all due reminders and create follow-up actions"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/reminders/process-due")
            response.raise_for_status()
            results = response.json()
        return {"processed": len(results), "results": results}
    except Exception as e:
        logger.error(f"Error processing due reminders: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba")
async def get_next_best_actions(customer_id: Optional[str] = None, limit: int = 10):
    """Get Next Best Actions (NBA) recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            params = {"limit": limit}
            if customer_id:
                params["customer_id"] = customer_id
            response = await client.get(f"{BACKEND_API_URL}/nba", params=params)
            response.raise_for_status()
            return response.json()
    except Exception as e:
        logger.error(f"Error fetching NBA recommendations: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nba/analyze")
async def analyze_customer_data():
    """Analyze customer data and generate NBA recommendations"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(f"{BACKEND_API_URL}/nba/analyze")
            response.raise_for_status()
            results = response.json()
        return {"analyzed": len(results), "recommendations": results}
    except Exception as e:
        logger.error(f"Error analyzing customer data: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-experimentation")
async def run_autonomous_experimentation():
    """Trigger a cycle of autonomous experimentation and self-modification."""
    try:
        logger.info("Initiating autonomous experimentation cycle...")
        self_modification_orchestrator.run_self_modification_cycle()
        logger.info("Autonomous experimentation cycle completed.")
        return {"status": "success", "message": "Autonomous experimentation cycle initiated."}
    except Exception as e:
        logger.error(f"Error during autonomous experimentation: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PYTHON_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
