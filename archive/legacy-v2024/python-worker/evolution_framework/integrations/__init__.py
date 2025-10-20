"""
Evolution Framework Integrations

Integration adapters for connecting the Evolution Framework with core services.
"""

from .nba_evolution_adapter import NBAEvolutionAdapter
from .reminder_evolution_adapter import ReminderEvolutionAdapter

__all__ = [
    "NBAEvolutionAdapter",
    "ReminderEvolutionAdapter",
]

