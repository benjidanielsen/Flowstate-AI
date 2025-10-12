"""
Evolution Framework

Self-improvement and continuous learning framework for Flowstate-AI.
"""

from .config import EvolutionConfig, default_config
from .metrics_collector import MetricsCollector
from .evolution_manager import EvolutionManager
from .knowledge_manager import VectorKnowledgeManager

__all__ = [
    "EvolutionConfig",
    "default_config",
    "MetricsCollector",
    "EvolutionManager",
    "VectorKnowledgeManager",
]

__version__ = "0.1.0"

