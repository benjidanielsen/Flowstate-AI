import json
import logging
import os
import asyncio
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx

# Import agent system
import sys
sys.path.append('/home/ubuntu/Flowstate-AI/python-worker')

from evolution_framework.specialized_agents import (
    CodeAnalyzerAgent,
    DataProcessorAgent,
    CoordinatorAgent,
    LearningAgent,
    MonitoringAgent,
)
from evolution_framework.self_modification_orchestrator import SelfModificationOrchestrator
from evolution_framework.evolution_governor import EvolutionGovernor
from evolution_framework.evolution_manager import FlowstateEvolutionManager
from evolution_framework.anomaly_detector import AnomalyDetector
from evolution_framework.metrics_collector import MetricsCollector

BACKEND_API_URL = os.getenv("BACKEND_API_URL", "http://localhost:3001")

app = FastAPI(title="Flowstate-AI Worker v2030", version="2.0.0")

# Initialize Evolution Framework components
metrics_collector = MetricsCollector("python_worker")
evolution_manager = FlowstateEvolutionManager()
anomaly_detector = AnomalyDetector(metrics_collector)
evolution_governor = EvolutionGovernor(evolution_manager, anomaly_detector, metrics_collector)
self_modification_orchestrator = SelfModificationOrchestrator(
    project_root="/home/ubuntu/Flowstate-AI", 
    config_path=None
)

# Initialize agents
agents = {}
agent_instances = []

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Pydantic models
class ReminderRequest(BaseModel):
    customer_id: str
    type: str
    message: str
    scheduled_for: datetime

class NBARequest(BaseModel):
    customer_id: Optional[str] = None
    limit: int = 10

class AgentTaskRequest(BaseModel):
    agent_name: str
    task_description: str
    context: Dict[str, Any]

class InterAgentMessageRequest(BaseModel):
    from_agent: str
    to_agent: str
    message: str
    message_type: str = "info"
    requires_response: bool = False


async def initialize_agents():
    """Initialize all agents and register them with the backend"""
    global agents, agent_instances
    
    logger.info("Initializing agent system...")
    
    try:
        # Create agent instances
        agent_instances = [
            CodeAnalyzerAgent(),
            DataProcessorAgent(),
            CoordinatorAgent(),
            LearningAgent(),
            MonitoringAgent(),
        ]
        
        # Register each agent
        for agent in agent_instances:
            try:
                result = await agent.register()
                agents[agent.agent_name] = agent
                logger.info(f"✓ Registered agent: {agent.agent_name}")
            except Exception as e:
                logger.error(f"✗ Failed to register agent {agent.agent_name}: {e}")
        
        logger.info(f"Agent system initialized with {len(agents)} agents")
        
    except Exception as e:
        logger.error(f"Failed to initialize agents: {e}")


async def start_job_processing():
    """Start background job processing for all agents"""
    logger.info("Starting background job processing...")
    
    async def process_agent_jobs():
        while True:
            try:
                for agent in agent_instances:
                    try:
                        results = await agent.process_jobs(max_jobs=3)
                        if results:
                            logger.info(f"Processed {len(results)} jobs for {agent.agent_name}")
                    except Exception as e:
                        logger.error(f"Error processing jobs for {agent.agent_name}: {e}")
                
                # Wait before next processing cycle
                await asyncio.sleep(10)
                
            except Exception as e:
                logger.error(f"Error in job processing cycle: {e}")
                await asyncio.sleep(30)
    
    # Start background task
    asyncio.create_task(process_agent_jobs())


@app.on_event("startup")
async def startup_event():
    """Initialize the agent system on startup"""
    await initialize_agents()
    await start_job_processing()


@app.get("/")
async def root():
    return {
        "message": "Flowstate-AI Python Worker v2030",
        "timestamp": datetime.now().isoformat(),
        "agents": list(agents.keys()),
    }


@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "agents": {name: "active" for name in agents.keys()},
    }


@app.get("/agents")
async def get_agents():
    """Get list of all agents and their capabilities"""
    agent_info = {}
    for name, agent in agents.items():
        agent_info[name] = {
            "capabilities": agent.capabilities,
            "status": "active",
        }
    return agent_info


@app.get("/agents/{agent_name}/status")
async def get_agent_status(agent_name: str):
    """Get status of a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    try:
        state = await agent.get_state()
        return {
            "agent_name": agent_name,
            "capabilities": agent.capabilities,
            "state": state,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_name}/task")
async def execute_agent_task(agent_name: str, request: AgentTaskRequest):
    """Execute a task on a specific agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    try:
        result = await agent.execute_task(request.task_description, request.context)
        return result
    except Exception as e:
        logger.error(f"Error executing task on {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/message")
async def send_inter_agent_message(request: InterAgentMessageRequest):
    """Send a message between agents"""
    if request.from_agent not in agents:
        raise HTTPException(status_code=404, detail="Source agent not found")
    
    from_agent = agents[request.from_agent]
    try:
        result = await from_agent.send_message(
            to_agent=request.to_agent,
            message=request.message,
            message_type=request.message_type,
            requires_response=request.requires_response,
        )
        return result
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/agents/{agent_name}/memory")
async def store_agent_memory(
    agent_name: str,
    content: str,
    memory_type: str = "general",
    tags: List[str] = [],
    importance: int = 5,
):
    """Store a memory for an agent"""
    if agent_name not in agents:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    agent = agents[agent_name]
    try:
        result = await agent.store_memory(
            content=content,
            memory_type=memory_type,
            tags=tags,
            importance=importance,
        )
        return result
    except Exception as e:
        logger.error(f"Error storing memory for {agent_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/workflow/coordinate")
async def coordinate_workflow(workflow: Dict[str, Any]):
    """Coordinate a multi-step workflow"""
    if "coordinator" not in agents:
        raise HTTPException(status_code=404, detail="Coordinator agent not found")
    
    coordinator = agents["coordinator"]
    try:
        result = await coordinator.coordinate_workflow(workflow)
        return result
    except Exception as e:
        logger.error(f"Error coordinating workflow: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/system/health-check")
async def system_health_check():
    """Perform a comprehensive system health check"""
    if "monitoring_agent" not in agents:
        raise HTTPException(status_code=404, detail="Monitoring agent not found")
    
    monitoring_agent = agents["monitoring_agent"]
    try:
        result = await monitoring_agent.perform_health_check()
        return result
    except Exception as e:
        logger.error(f"Error performing health check: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Legacy endpoints for backward compatibility
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


# AI task endpoints for backward compatibility
@app.post("/ai-task/{task_type}")
async def ai_task(task_type: str, payload: Dict[str, Any]):
    """Execute an AI task (backward compatibility)"""
    try:
        # Route to appropriate agent based on task type
        if task_type in ["code_analysis", "analyze_code", "detect_bugs"]:
            if "code_analyzer" in agents:
                return await agents["code_analyzer"].execute_task(f"AI task: {task_type}", payload)
        elif task_type in ["data_processing", "process_data", "validate_data"]:
            if "data_processor" in agents:
                return await agents["data_processor"].execute_task(f"AI task: {task_type}", payload)
        elif task_type in ["coordination", "delegate_task"]:
            if "coordinator" in agents:
                return await agents["coordinator"].execute_task(f"AI task: {task_type}", payload)
        
        # Default to coordinator if no specific agent matches
        if "coordinator" in agents:
            return await agents["coordinator"].execute_task(f"AI task: {task_type}", payload)
        
        return {"status": "no_suitable_agent", "task_type": task_type}
        
    except Exception as e:
        logger.error(f"Error executing AI task {task_type}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    port = int(os.getenv("PYTHON_API_PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
