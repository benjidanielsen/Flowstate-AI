"""Lightweight in-memory knowledge manager used during development tests."""
from __future__ import annotations

import logging
import math
import uuid
from collections import Counter
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from .config import EvolutionConfig


@dataclass
class _KnowledgeEntry:
    id: str
    content: str
    category: str
    source: str
    confidence: float
    timestamp: str
    usage_count: int
    last_accessed: str
    metadata: Dict[str, Any]
    vector: Counter


def _tokenize(text: str) -> Counter:
    tokens = [token.lower() for token in text.split() if token]
    return Counter(tokens)


def _cosine_similarity(vec1: Counter, vec2: Counter) -> float:
    if not vec1 or not vec2:
        return 0.0

    intersection = set(vec1) & set(vec2)
    dot_product = sum(vec1[token] * vec2[token] for token in intersection)
    norm1 = math.sqrt(sum(value * value for value in vec1.values()))
    norm2 = math.sqrt(sum(value * value for value in vec2.values()))
    if norm1 == 0 or norm2 == 0:
        return 0.0
    return dot_product / (norm1 * norm2)


class VectorKnowledgeManager:
    """Minimal knowledge manager with cosine similarity search."""

    def __init__(self, config: Optional[EvolutionConfig] = None):
        self.config = config or EvolutionConfig()
        self.logger = logging.getLogger("knowledge_manager")
        self._store: Dict[str, _KnowledgeEntry] = {}
        self.logger.info("Initialized in-memory knowledge manager")

    # API compatibility helpers -------------------------------------------------
    def _ensure_collection(self) -> None:  # pragma: no cover - placeholder
        """Maintained for compatibility with the original interface."""
        return None

    # CRUD operations -----------------------------------------------------------
    def add_knowledge(
        self,
        content: str,
        category: str,
        source: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        knowledge_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()
        entry = _KnowledgeEntry(
            id=knowledge_id,
            content=content,
            category=category,
            source=source,
            confidence=confidence,
            timestamp=timestamp,
            usage_count=0,
            last_accessed=timestamp,
            metadata=dict(metadata or {}),
            vector=_tokenize(content),
        )
        self._store[knowledge_id] = entry
        self.logger.debug("Added knowledge entry %s", knowledge_id)
        return knowledge_id

    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 5,
        min_confidence: float = 0.0,
    ) -> List[Dict[str, Any]]:
        query_vector = _tokenize(query)
        candidates = []
        for entry in self._store.values():
            if category and entry.category != category:
                continue
            if source and entry.source != source:
                continue
            if entry.confidence < min_confidence:
                continue
            score = _cosine_similarity(query_vector, entry.vector)
            if score > 0:
                candidates.append((score, entry))

        candidates.sort(key=lambda item: item[0], reverse=True)
        results = []
        for score, entry in candidates[:limit]:
            self._touch(entry.id)
            results.append(
                {
                    "id": entry.id,
                    "score": score,
                    "content": entry.content,
                    "category": entry.category,
                    "source": entry.source,
                    "confidence": entry.confidence,
                    "timestamp": entry.timestamp,
                    "usage_count": entry.usage_count,
                    "last_accessed": entry.last_accessed,
                    **entry.metadata,
                }
            )
        return results

    def _touch(self, knowledge_id: str) -> None:
        entry = self._store.get(knowledge_id)
        if entry:
            entry.usage_count += 1
            entry.last_accessed = datetime.now().isoformat()

    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        entry = self._store.get(knowledge_id)
        if not entry:
            return None
        self._touch(knowledge_id)
        return {
            "id": entry.id,
            "content": entry.content,
            "category": entry.category,
            "source": entry.source,
            "confidence": entry.confidence,
            "timestamp": entry.timestamp,
            "usage_count": entry.usage_count,
            "last_accessed": entry.last_accessed,
            **entry.metadata,
        }

    def update_knowledge(
        self,
        knowledge_id: str,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        entry = self._store.get(knowledge_id)
        if not entry:
            self.logger.warning("Knowledge entry not found: %s", knowledge_id)
            return False
        if confidence is not None:
            entry.confidence = confidence
        if metadata:
            entry.metadata.update(metadata)
        self.logger.debug("Updated knowledge entry %s", knowledge_id)
        return True

    def delete_knowledge(self, knowledge_id: str) -> bool:
        if knowledge_id in self._store:
            del self._store[knowledge_id]
            self.logger.debug("Deleted knowledge entry %s", knowledge_id)
            return True
        return False

    def cleanup_old_knowledge(self, days: Optional[int] = None) -> int:
        retention_days = days or self.config.knowledge_retention_days
        cutoff = datetime.now() - timedelta(days=retention_days)
        to_delete = [
            knowledge_id
            for knowledge_id, entry in self._store.items()
            if entry.timestamp < cutoff.isoformat()
        ]
        for knowledge_id in to_delete:
            self.delete_knowledge(knowledge_id)
        return len(to_delete)

    def get_knowledge_stats(self) -> Dict[str, Any]:
        category_counts: Dict[str, int] = {}
        for entry in self._store.values():
            category_counts[entry.category] = category_counts.get(entry.category, 0) + 1
        return {
            "total_entries": len(self._store),
            "vector_dimension": 0,
            "category_distribution": category_counts,
        }

    # Compatibility hooks ------------------------------------------------------
    def search(self, *args, **kwargs):  # pragma: no cover - for compatibility
        raise NotImplementedError("Direct search API not implemented in stub")

    def retrieve(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Direct retrieve API not implemented in stub")

    def set_payload(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Direct set_payload API not implemented in stub")

    def delete(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Direct delete API not implemented in stub")

    def scroll(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Direct scroll API not implemented in stub")

    def get_collection(self, *args, **kwargs):  # pragma: no cover
        raise NotImplementedError("Direct get_collection API not implemented in stub")

