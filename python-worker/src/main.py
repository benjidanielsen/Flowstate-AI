from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uvicorn
import os
from datetime import datetime, timedelta, timezone
import sqlite3
import json
from services.reminder_service import ReminderService
from services.nba_service import NBAService

app = FastAPI(title="Flowstate-AI Worker", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
reminder_service = ReminderService()
nba_service = NBAService()

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
    return {"message": "Flowstate-AI Python Worker", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/reminders")
async def create_reminder(reminder: ReminderRequest):
    """Create a new reminder"""
    try:
        result = await reminder_service.create_reminder(
            customer_id=reminder.customer_id,
            reminder_type=reminder.type,
            message=reminder.message,
            scheduled_for=reminder.scheduled_for
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/reminders/due")
async def get_due_reminders():
    """Get all reminders that are due"""
    try:
        return await reminder_service.get_due_reminders()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/{reminder_id}/complete")
async def complete_reminder(reminder_id: str):
    """Mark a reminder as complete"""
    try:
        result = await reminder_service.complete_reminder(reminder_id)
        if not result:
            raise HTTPException(status_code=404, detail="Reminder not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/reminders/process-due")
async def process_due_reminders():
    """Process all due reminders and create follow-up actions"""
    try:
        results = await reminder_service.process_due_reminders()
        return {"processed": len(results), "results": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/nba")
async def get_next_best_actions(customer_id: Optional[str] = None, limit: int = 10):
    """Get Next Best Actions (NBA) recommendations"""
    try:
        return await nba_service.get_recommendations(customer_id=customer_id, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/nba/analyze")
async def analyze_customer_data():
    """Analyze customer data and generate NBA recommendations"""
    try:
        results = await nba_service.analyze_and_generate_recommendations()
        return {"analyzed": len(results), "recommendations": results}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)