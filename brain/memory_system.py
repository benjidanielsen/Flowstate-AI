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

    def add_context(self, category, context_key, context_value):
        """
        Add contextual information to a memory category.
        
        Args:
            category: Memory category
            context_key: Key for the contextual information
            context_value: Value of the contextual information
        """
        with self._lock:
            context_category = f"{category}_context"
            context_entry = {context_key: context_value}
            
            # Check if context already exists
            existing_contexts = self._memory.get(context_category, [])
            updated = False
            
            for i, ctx in enumerate(existing_contexts):
                if isinstance(ctx, dict) and context_key in ctx:
                    existing_contexts[i][context_key] = context_value
                    updated = True
                    break
            
            if not updated:
                self._memory[context_category].append(context_entry)
            
            self._save_memory()
    
    def get_context(self, category, context_key=None):
        """
        Retrieve contextual information for a memory category.
        
        Args:
            category: Memory category
            context_key: Optional specific context key to retrieve
            
        Returns:
            Context value(s) or None if not found
        """
        with self._lock:
            context_category = f"{category}_context"
            contexts = self._memory.get(context_category, [])
            
            if context_key:
                for ctx in contexts:
                    if isinstance(ctx, dict) and context_key in ctx:
                        return ctx[context_key]
                return None
            else:
                return contexts
    
    def consolidate_memories(self, category):
        """
        Consolidate similar memories in a category to reduce redundancy.
        
        Args:
            category: Memory category to consolidate
            
        Returns:
            Number of memories removed
        """
        with self._lock:
            learnings = self._memory.get(category, [])
            if len(learnings) <= 1:
                return 0
            
            # Simple consolidation: remove exact duplicates and very similar entries
            unique_learnings = []
            removed_count = 0
            
            for learning in learnings:
                is_duplicate = False
                learning_lower = learning.lower()
                
                for existing in unique_learnings:
                    existing_lower = existing.lower()
                    # Check for exact match or high similarity
                    if learning_lower == existing_lower:
                        is_duplicate = True
                        removed_count += 1
                        break
                    
                    # Check for substring containment (one is subset of other)
                    if learning_lower in existing_lower or existing_lower in learning_lower:
                        # Keep the longer, more detailed one
                        if len(learning) > len(existing):
                            unique_learnings.remove(existing)
                            unique_learnings.append(learning)
                        is_duplicate = True
                        removed_count += 1
                        break
                
                if not is_duplicate:
                    unique_learnings.append(learning)
            
            self._memory[category] = unique_learnings
            self._save_memory()
            return removed_count
    
    def get_memory_stats(self):
        """
        Get statistics about the memory system.
        
        Returns:
            Dictionary with memory statistics
        """
        with self._lock:
            total_learnings = sum(len(v) for v in self._memory.values())
            categories = list(self._memory.keys())
            
            category_sizes = {
                category: len(learnings)
                for category, learnings in self._memory.items()
            }
            
            # Sort categories by size
            top_categories = sorted(
                category_sizes.items(),
                key=lambda x: x[1],
                reverse=True
            )[:5]
            
            return {
                'total_learnings': total_learnings,
                'total_categories': len(categories),
                'categories': categories,
                'top_categories': dict(top_categories),
                'average_learnings_per_category': round(total_learnings / len(categories), 2) if categories else 0
            }
    
    def export_memory(self, category=None, format='json'):
        """
        Export memory data in various formats.
        
        Args:
            category: Optional category to export (None for all)
            format: Export format ('json', 'text', 'markdown')
            
        Returns:
            Exported data as string
        """
        with self._lock:
            if category:
                data = {category: self._memory.get(category, [])}
            else:
                data = dict(self._memory)
            
            if format == 'json':
                return json.dumps(data, indent=2, ensure_ascii=False)
            
            elif format == 'text':
                lines = []
                for cat, learnings in data.items():
                    lines.append(f"Category: {cat}")
                    for learning in learnings:
                        lines.append(f"  - {learning}")
                    lines.append("")
                return "\n".join(lines)
            
            elif format == 'markdown':
                lines = ["# Memory System Export\n"]
                for cat, learnings in data.items():
                    lines.append(f"## {cat}\n")
                    for learning in learnings:
                        lines.append(f"- {learning}")
                    lines.append("")
                return "\n".join(lines)
            
            else:
                raise ValueError(f"Unsupported format: {format}")
    
    def import_memory(self, data, format='json', merge=True):
        """
        Import memory data from various formats.
        
        Args:
            data: Data to import (string)
            format: Import format ('json')
            merge: If True, merge with existing data; if False, replace
            
        Returns:
            Number of learnings imported
        """
        with self._lock:
            if format == 'json':
                imported_data = json.loads(data)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            count = 0
            
            if not merge:
                self._memory.clear()
            
            for category, learnings in imported_data.items():
                if isinstance(learnings, list):
                    for learning in learnings:
                        if learning not in self._memory[category]:
                            self._memory[category].append(learning)
                            count += 1
                else:
                    if learnings not in self._memory[category]:
                        self._memory[category].append(learnings)
                        count += 1
            
            self._save_memory()
            return count
    
    def search_memories(self, query, limit=10):
        """
        Search memories using a query string with relevance scoring.
        
        Args:
            query: Search query
            limit: Maximum number of results to return
            
        Returns:
            List of tuples (category, learning, relevance_score)
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())
        results = []
        
        with self._lock:
            for category, learnings in self._memory.items():
                for learning in learnings:
                    learning_lower = learning.lower()
                    
                    # Calculate relevance score
                    score = 0
                    
                    # Exact match gets highest score
                    if query_lower == learning_lower:
                        score = 100
                    # Substring match
                    elif query_lower in learning_lower:
                        score = 75
                    else:
                        # Word overlap scoring
                        learning_words = set(learning_lower.split())
                        common_words = query_words & learning_words
                        if common_words:
                            score = (len(common_words) / len(query_words)) * 50
                    
                    if score > 0:
                        results.append((category, learning, score))
            
            # Sort by relevance score (descending)
            results.sort(key=lambda x: x[2], reverse=True)
            return results[:limit]


# Update singleton instance
memory_system = MemorySystem()
