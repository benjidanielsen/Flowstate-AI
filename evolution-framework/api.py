"""
Evolution Framework API - FastAPI service layer

Exposes evolution, knowledge management, and anomaly detection capabilities
through a REST API.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn

from evolution_manager import EvolutionManager, ComponentGenome, EvolutionStatus
from knowledge_manager import VectorKnowledgeManager
from anomaly_detector import AnomalyDetector, AnomalySeverity

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Flowstate-AI Evolution Framework",
    description="Self-evolving AI system with genetic algorithms, vector knowledge, and anomaly detection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core components
evolution_manager = EvolutionManager(
    mutation_rate=0.1,
    crossover_rate=0.7,
    population_size=10,
    elite_size=2,
    max_generations=50,
    fitness_threshold=0.8,
    enable_auto_deploy=False
)

knowledge_manager = VectorKnowledgeManager(
    embedding_model="all-MiniLM-L6-v2",
    index_type="Flat",
    storage_path="./knowledge_base"
)

anomaly_detector = AnomalyDetector(
    window_size=1000,
    detection_threshold=3.0,
    min_samples=30,
    alert_cooldown=300
)


# Pydantic models for API
class ComponentGenomeRequest(BaseModel):
    component_id: str
    version: str
    genes: Dict[str, Any]
    fitness_score: float = 0.0
    generation: int = 0


class EvolutionRequest(BaseModel):
    component_id: str
    target_metric: Optional[str] = None
    target_improvement: float = 0.1


class KnowledgeRequest(BaseModel):
    content: str
    metadata: Optional[Dict[str, Any]] = None
    category: str = "general"
    source: str = "api"
    confidence: float = 1.0


class KnowledgeSearchRequest(BaseModel):
    query: str
    top_k: int = 5
    category_filter: Optional[str] = None
    min_confidence: float = 0.0


class MetricRequest(BaseModel):
    metric_name: str
    value: float
    context: Optional[Dict[str, Any]] = None


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    components: Dict[str, str]


# Health check endpoint
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "evolution_manager": "operational",
            "knowledge_manager": "operational" if knowledge_manager._initialized else "initializing",
            "anomaly_detector": "operational"
        }
    }


# Evolution Manager endpoints
@app.post("/evolution/components/register")
async def register_component(genome_request: ComponentGenomeRequest):
    """Register a component for evolution"""
    try:
        genome = ComponentGenome(
            component_id=genome_request.component_id,
            version=genome_request.version,
            genes=genome_request.genes,
            fitness_score=genome_request.fitness_score,
            generation=genome_request.generation
        )
        
        evolution_manager.register_component(genome)
        
        return {
            "success": True,
            "message": f"Component {genome_request.component_id} registered successfully",
            "genome_hash": genome.get_hash()
        }
    
    except Exception as e:
        logger.error(f"Failed to register component: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evolution/evolve")
async def evolve_component(
    evolution_request: EvolutionRequest,
    background_tasks: BackgroundTasks
):
    """Trigger evolution for a component"""
    try:
        # Run evolution in background
        cycle = await evolution_manager.evolve_component(
            component_id=evolution_request.component_id,
            target_metric=evolution_request.target_metric,
            target_improvement=evolution_request.target_improvement
        )
        
        return {
            "success": True,
            "cycle_id": cycle.cycle_id,
            "status": cycle.status.value,
            "fitness_improvement": (
                cycle.candidate_genomes[0].fitness_score - cycle.current_genome.fitness_score
                if cycle.candidate_genomes else 0.0
            ),
            "safety_checks": cycle.safety_checks
        }
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Evolution failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evolution/history")
async def get_evolution_history(component_id: Optional[str] = None):
    """Get evolution history"""
    try:
        history = evolution_manager.get_evolution_history(component_id)
        return {
            "success": True,
            "count": len(history),
            "history": history
        }
    except Exception as e:
        logger.error(f"Failed to get history: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/evolution/components")
async def list_components():
    """List all registered components"""
    try:
        components = [
            {
                "component_id": genome.component_id,
                "version": genome.version,
                "fitness_score": genome.fitness_score,
                "generation": genome.generation,
                "genome_hash": genome.get_hash()
            }
            for genome in evolution_manager.components.values()
        ]
        
        return {
            "success": True,
            "count": len(components),
            "components": components
        }
    except Exception as e:
        logger.error(f"Failed to list components: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Knowledge Manager endpoints
@app.post("/knowledge/add")
async def add_knowledge(knowledge_request: KnowledgeRequest):
    """Add new knowledge entry"""
    try:
        entry_id = await knowledge_manager.add_knowledge(
            content=knowledge_request.content,
            metadata=knowledge_request.metadata,
            category=knowledge_request.category,
            source=knowledge_request.source,
            confidence=knowledge_request.confidence
        )
        
        return {
            "success": True,
            "entry_id": entry_id,
            "message": "Knowledge added successfully"
        }
    
    except Exception as e:
        logger.error(f"Failed to add knowledge: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/knowledge/search")
async def search_knowledge(search_request: KnowledgeSearchRequest):
    """Search for relevant knowledge"""
    try:
        results = await knowledge_manager.search_knowledge(
            query=search_request.query,
            top_k=search_request.top_k,
            category_filter=search_request.category_filter,
            min_confidence=search_request.min_confidence
        )
        
        formatted_results = [
            {
                "entry_id": entry.entry_id,
                "content": entry.content,
                "category": entry.category,
                "source": entry.source,
                "confidence": entry.confidence,
                "similarity_score": float(similarity),
                "metadata": entry.metadata,
                "access_count": entry.access_count
            }
            for entry, similarity in results
        ]
        
        return {
            "success": True,
            "count": len(formatted_results),
            "results": formatted_results
        }
    
    except Exception as e:
        logger.error(f"Knowledge search failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/knowledge/stats")
async def get_knowledge_stats():
    """Get knowledge base statistics"""
    try:
        stats = await knowledge_manager.get_knowledge_stats()
        
        # Format most accessed entries
        if "most_accessed" in stats:
            stats["most_accessed"] = [
                {
                    "entry_id": entry.entry_id,
                    "category": entry.category,
                    "access_count": entry.access_count
                }
                for entry in stats["most_accessed"]
            ]
        
        return {
            "success": True,
            "stats": stats
        }
    
    except Exception as e:
        logger.error(f"Failed to get knowledge stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Anomaly Detector endpoints
@app.post("/anomaly/record")
async def record_metric(metric_request: MetricRequest):
    """Record a metric and check for anomalies"""
    try:
        anomaly = await anomaly_detector.record_metric(
            metric_name=metric_request.metric_name,
            value=metric_request.value,
            context=metric_request.context
        )
        
        if anomaly:
            return {
                "success": True,
                "anomaly_detected": True,
                "anomaly": anomaly.to_dict()
            }
        else:
            return {
                "success": True,
                "anomaly_detected": False,
                "message": "Metric recorded successfully"
            }
    
    except Exception as e:
        logger.error(f"Failed to record metric: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomaly/recent")
async def get_recent_anomalies(
    metric_name: Optional[str] = None,
    severity: Optional[str] = None,
    hours: int = 24,
    include_resolved: bool = False
):
    """Get recent anomalies"""
    try:
        # Convert severity string to enum
        severity_enum = None
        if severity:
            try:
                severity_enum = AnomalySeverity(severity.lower())
            except ValueError:
                raise HTTPException(status_code=400, detail=f"Invalid severity: {severity}")
        
        anomalies = await anomaly_detector.get_recent_anomalies(
            metric_name=metric_name,
            severity=severity_enum,
            hours=hours,
            include_resolved=include_resolved
        )
        
        return {
            "success": True,
            "count": len(anomalies),
            "anomalies": [anomaly.to_dict() for anomaly in anomalies]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get anomalies: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomaly/summary")
async def get_anomaly_summary():
    """Get anomaly summary"""
    try:
        summary = await anomaly_detector.get_anomaly_summary()
        
        return {
            "success": True,
            "summary": summary
        }
    
    except Exception as e:
        logger.error(f"Failed to get anomaly summary: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/anomaly/resolve/{anomaly_id}")
async def resolve_anomaly(anomaly_id: str):
    """Mark an anomaly as resolved"""
    try:
        success = await anomaly_detector.resolve_anomaly(anomaly_id)
        
        if success:
            return {
                "success": True,
                "message": f"Anomaly {anomaly_id} resolved"
            }
        else:
            raise HTTPException(status_code=404, detail=f"Anomaly {anomaly_id} not found")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to resolve anomaly: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/anomaly/metrics/{metric_name}/stats")
async def get_metric_stats(metric_name: str):
    """Get statistical summary for a metric"""
    try:
        stats = await anomaly_detector.get_metric_stats(metric_name)
        
        if stats:
            return {
                "success": True,
                "stats": {
                    "metric_name": stats.metric_name,
                    "count": stats.count,
                    "mean": stats.mean,
                    "std": stats.std,
                    "min": stats.min,
                    "max": stats.max,
                    "percentiles": {
                        "25": stats.percentile_25,
                        "50": stats.percentile_50,
                        "75": stats.percentile_75,
                        "95": stats.percentile_95,
                        "99": stats.percentile_99
                    },
                    "expected_range": stats.get_expected_range()
                }
            }
        else:
            raise HTTPException(status_code=404, detail=f"No stats available for metric: {metric_name}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get metric stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize components on startup"""
    logger.info("Starting Evolution Framework API...")
    
    # Initialize knowledge manager
    await knowledge_manager.initialize()
    
    logger.info("Evolution Framework API started successfully")


# Main entry point
if __name__ == "__main__":
    uvicorn.run(
        "api:app",
        host="0.0.0.0",
        port=9000,
        reload=True,
        log_level="info"
    )

