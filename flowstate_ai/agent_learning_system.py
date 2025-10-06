import json
import os
from typing import Dict, Any

class AgentLearningSystem:
    """
    Agent Learning System that tracks agent successes and failures,
    updates experience data, and adapts agent behavior accordingly.
    """

    DATA_FILE = "agent_experience.json"

    def __init__(self, data_path: str = None):
        """
        Initialize the learning system, loading experience data if available.
        """
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), self.DATA_FILE)
        self.experience = {
            "successes": 0,
            "failures": 0,
            "history": []  # list of dicts with keys: outcome, details
        }
        self.load_experience()

    def load_experience(self):
        """Load experience data from file."""
        if os.path.exists(self.data_path):
            try:
                with open(self.data_path, "r", encoding="utf-8") as f:
                    self.experience = json.load(f)
            except Exception as e:
                print(f"Warning: Failed to load experience data: {e}")

    def save_experience(self):
        """Save experience data to file."""
        try:
            with open(self.data_path, "w", encoding="utf-8") as f:
                json.dump(self.experience, f, indent=2)
        except Exception as e:
            print(f"Warning: Failed to save experience data: {e}")

    def record_success(self, details: Dict[str, Any] = None):
        """Record a success event with optional details."""
        self.experience["successes"] += 1
        self.experience["history"].append({"outcome": "success", "details": details or {}})
        self.save_experience()

    def record_failure(self, details: Dict[str, Any] = None):
        """Record a failure event with optional details."""
        self.experience["failures"] += 1
        self.experience["history"].append({"outcome": "failure", "details": details or {}})
        self.save_experience()

    def get_success_rate(self) -> float:
        """Calculate and return the success rate as a float between 0 and 1."""
        total = self.experience["successes"] + self.experience["failures"]
        if total == 0:
            return 0.0
        return self.experience["successes"] / total

    def adapt_behavior(self) -> Dict[str, Any]:
        """
        Adapt agent behavior based on success rate and history.
        This is a placeholder for actual adaptive logic.

        Returns a dict representing adapted parameters.
        """
        success_rate = self.get_success_rate()

        # Simple example adaptation:
        if success_rate > 0.8:
            behavior = {"aggressiveness": "high", "exploration": "low"}
        elif success_rate > 0.5:
            behavior = {"aggressiveness": "medium", "exploration": "medium"}
        else:
            behavior = {"aggressiveness": "low", "exploration": "high"}

        return behavior

# Example usage:
# als = AgentLearningSystem()
# als.record_success({"task": "navigate maze"})
# als.record_failure({"task": "open door"})
# print(f"Success rate: {als.get_success_rate():.2f}")
# adapted_params = als.adapt_behavior()
# print(f"Adapted behavior: {adapted_params}")
