import threading
from collections import defaultdict
import json
import os

class MemorySystem:
    """
    Collective memory system for all agents.
    Stores learnings and patterns.
    Thread-safe implementation to allow concurrent access.
    """

    def __init__(self, storage_path='memory_storage.json'):
        self._lock = threading.Lock()
        self._memory = defaultdict(list)  # key: category/topic, value: list of learnings/patterns
        self.storage_path = storage_path
        self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    for key, val in data.items():
                        if isinstance(val, list):
                            self._memory[key] = val
                        else:
                            self._memory[key] = [val]
            except Exception:
                # If corrupted or unreadable file, start fresh
                self._memory = defaultdict(list)

    def _save_memory(self):
        with open(self.storage_path, 'w', encoding='utf-8') as f:
            json.dump(self._memory, f, indent=2, ensure_ascii=False)

    def add_learning(self, category, learning):
        """
        Add a learning or pattern under a specific category.

        :param category: str - the topic or category of the learning
        :param learning: str - the learning or pattern to store
        """
        with self._lock:
            if learning not in self._memory[category]:
                self._memory[category].append(learning)
                self._save_memory()

    def get_learnings(self, category=None):
        """
        Retrieve all learnings or those under a specific category.

        :param category: str or None - if None, returns all learnings grouped by category
        :return: dict or list - dictionary of categories to learnings or list of learnings
        """
        with self._lock:
            if category:
                return list(self._memory.get(category, []))
            else:
                # Return a copy to avoid external mutation
                return {k: list(v) for k, v in self._memory.items()}

    def find_patterns(self, keyword):
        """
        Search the memory for learnings containing a keyword.

        :param keyword: str - keyword to search for
        :return: dict - categories mapped to matching learnings
        """
        keyword_lower = keyword.lower()
        matches = {}
        with self._lock:
            for category, learnings in self._memory.items():
                filtered = [l for l in learnings if keyword_lower in l.lower()]
                if filtered:
                    matches[category] = filtered
        return matches

    def clear_memory(self):
        """
        Clear all stored memories.
        """
        with self._lock:
            self._memory.clear()
            self._save_memory()


# Singleton instance to be used across agents
memory_system = MemorySystem()
