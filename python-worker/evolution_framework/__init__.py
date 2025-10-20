"""Evolution Framework package with lazy attribute loading."""
from __future__ import annotations

import importlib
from typing import Any, Dict

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

_MODULE_MAP: Dict[str, str] = {
    "EvolutionConfig": "evolution_framework.config",
    "default_config": "evolution_framework.config",
    "MetricsCollector": "evolution_framework.metrics_collector",
    "EvolutionManager": "evolution_framework.evolution_manager",
    "VectorKnowledgeManager": "evolution_framework.knowledge_manager",
    "CodeAnalyzer": "evolution_framework.code_analyzer",
    "SelfModificationOrchestrator": "evolution_framework.self_modification_orchestrator",
    "AnomalyDetector": "evolution_framework.anomaly_detector",
    "EvolutionGovernor": "evolution_framework.evolution_governor",
    "CrossDomainLearner": "evolution_framework.cross_domain_learner",
    "MetaOptimizer": "evolution_framework.meta_optimizer",
    "EdgeCaseManager": "evolution_framework.edge_case_manager",
    "PredictiveOptimizer": "evolution_framework.predictive_optimizer",
    "XAINBA": "evolution_framework.xai_nba",
    "MultiAgentCoordinator": "evolution_framework.multi_agent_coordinator",
    "HumanOversightManager": "evolution_framework.human_oversight_manager",
    "PerformanceTuner": "evolution_framework.performance_tuner",
    "CostOptimizer": "evolution_framework.cost_optimizer",
}


def __getattr__(name: str) -> Any:
    if name not in _MODULE_MAP:
        raise AttributeError(f"module 'evolution_framework' has no attribute '{name}'")

    module = importlib.import_module(_MODULE_MAP[name])
    return getattr(module, name)


__version__ = "0.2.0"
