"""
Evolution Framework

Self-improvement and continuous learning framework for Flowstate-AI.
"""

from .config import EvolutionConfig, default_config
from .metrics_collector import MetricsCollector
from .evolution_manager import EvolutionManager
from .knowledge_manager import VectorKnowledgeManager
from .code_analyzer import CodeAnalyzer
from .self_modification_orchestrator import SelfModificationOrchestrator
from .anomaly_detector import AnomalyDetector
from .evolution_governor import EvolutionGovernor
from .cross_domain_learner import CrossDomainLearner
from .meta_optimizer import MetaOptimizer
from .edge_case_manager import EdgeCaseManager
from .predictive_optimizer import PredictiveOptimizer
from .xai_nba import XAINBA
from .multi_agent_coordinator import MultiAgentCoordinator
from .human_oversight_manager import HumanOversightManager
from .performance_tuner import PerformanceTuner
from .cost_optimizer import CostOptimizer

__all__ = [
    "EvolutionConfig",
    "default_config",
    "MetricsCollector",
    "EvolutionManager",
    "VectorKnowledgeManager",
    "CodeAnalyzer",
    "SelfModificationOrchestrator",
    "AnomalyDetector",
    "EvolutionGovernor",
    "CrossDomainLearner",
    "MetaOptimizer",
    "EdgeCaseManager",
    "PredictiveOptimizer",
    "XAINBA",
    "MultiAgentCoordinator",
    "HumanOversightManager",
    "PerformanceTuner",
    "CostOptimizer",
]

__version__ = "0.2.0"

