"""
Evolution Framework Configuration

This module defines the configuration settings for the Flowstate-AI Evolution Framework.
"""

import os
from typing import Dict, Any, List
from dataclasses import dataclass, field


@dataclass
class EvolutionConfig:
    """Configuration for the Evolution Framework."""
    
    # Master switches
    enabled: bool = True
    safe_mode: bool = False
    
    # Thresholds
    auto_apply_threshold: float = 0.8  # Confidence threshold for automatic application
    anomaly_threshold: float = 2.0  # Z-score threshold for anomaly detection
    metrics_window: int = 100  # Number of data points for statistical analysis
    
    # Knowledge management
    knowledge_retention_days: int = 365
    vector_db_host: str = field(default_factory=lambda: os.getenv("VECTOR_DB_HOST", "localhost"))
    vector_db_port: int = field(default_factory=lambda: int(os.getenv("VECTOR_DB_PORT", "6333")))
    vector_db_collection: str = "flowstate_knowledge"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"  # Local model
    
    # Cost management
    cost_budget_daily_limit: float = 10.0  # USD
    cost_budget_per_operation_limit: float = 0.50  # USD
    use_local_llm: bool = True  # Prioritize local LLMs for cost savings
    local_llm_endpoint: str = field(default_factory=lambda: os.getenv("LOCAL_LLM_ENDPOINT", "http://localhost:11434"))
    
    # Modification boundaries
    allowed_modifications: List[str] = field(default_factory=lambda: [
        "nba_engine",
        "reminder_system",
        "analytics",
        "ui_components"
    ])
    
    human_oversight_required: List[str] = field(default_factory=lambda: [
        "database_schema",
        "authentication",
        "security_policies",
        "billing"
    ])
    
    # Evolution cycle settings
    cycle_interval_minutes: int = 60  # How often to run evolution cycles
    max_modifications_per_cycle: int = 3
    require_validation: bool = True
    
    # Monitoring and logging
    log_level: str = field(default_factory=lambda: os.getenv("LOG_LEVEL", "INFO"))
    metrics_retention_days: int = 90
    enable_detailed_logging: bool = True
    
    # Database connection
    database_url: str = field(default_factory=lambda: os.getenv("DATABASE_URL", ""))
    
    @classmethod
    def from_dict(cls, config_dict: Dict[str, Any]) -> "EvolutionConfig":
        """Create configuration from dictionary."""
        return cls(**config_dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "enabled": self.enabled,
            "safe_mode": self.safe_mode,
            "auto_apply_threshold": self.auto_apply_threshold,
            "anomaly_threshold": self.anomaly_threshold,
            "metrics_window": self.metrics_window,
            "knowledge_retention_days": self.knowledge_retention_days,
            "vector_db_host": self.vector_db_host,
            "vector_db_port": self.vector_db_port,
            "vector_db_collection": self.vector_db_collection,
            "embedding_model": self.embedding_model,
            "cost_budget_daily_limit": self.cost_budget_daily_limit,
            "cost_budget_per_operation_limit": self.cost_budget_per_operation_limit,
            "use_local_llm": self.use_local_llm,
            "local_llm_endpoint": self.local_llm_endpoint,
            "allowed_modifications": self.allowed_modifications,
            "human_oversight_required": self.human_oversight_required,
            "cycle_interval_minutes": self.cycle_interval_minutes,
            "max_modifications_per_cycle": self.max_modifications_per_cycle,
            "require_validation": self.require_validation,
            "log_level": self.log_level,
            "metrics_retention_days": self.metrics_retention_days,
            "enable_detailed_logging": self.enable_detailed_logging,
            "database_url": self.database_url
        }
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        if self.auto_apply_threshold < 0 or self.auto_apply_threshold > 1:
            raise ValueError("auto_apply_threshold must be between 0 and 1")
        
        if self.anomaly_threshold < 0:
            raise ValueError("anomaly_threshold must be positive")
        
        if self.metrics_window < 10:
            raise ValueError("metrics_window must be at least 10")
        
        if not self.database_url:
            raise ValueError("database_url is required")
        
        return True


# Default configuration instance
default_config = EvolutionConfig()

