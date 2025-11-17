"""
Vector Knowledge Manager

Manages persistent knowledge storage using vector embeddings for semantic search.
"""

import logging
import math
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

try:  # pragma: no cover - exercised indirectly
    from sentence_transformers import SentenceTransformer
except Exception:  # pragma: no cover - deterministic fallback
    SentenceTransformer = None  # type: ignore[assignment]

try:  # pragma: no cover
    from qdrant_client import QdrantClient
    from qdrant_client.models import (
        Distance,
        VectorParams,
        PointStruct,
        Filter,
        FieldCondition,
        MatchValue,
    )
except Exception:  # pragma: no cover - deterministic fallback
    QdrantClient = None  # type: ignore[assignment]
    Distance = VectorParams = PointStruct = Filter = FieldCondition = MatchValue = None  # type: ignore[assignment]
from .config import EvolutionConfig


class VectorKnowledgeManager:
    """Manages knowledge storage and retrieval using vector embeddings."""
    
    def __init__(self, config: Optional[EvolutionConfig] = None):
        """
        Initialize the knowledge manager.
        
        Args:
            config: Evolution framework configuration
        """
        self.config = config or EvolutionConfig()
        self.logger = logging.getLogger("knowledge_manager")
        
        self._using_memory_backend = (
            SentenceTransformer is None or QdrantClient is None
        )
        self._memory_store: Dict[str, Dict[str, Any]] = {}

        if self._using_memory_backend:
            self.embedding_model = None
            self.embedding_dim = 64
            self.client = None
            self.logger.warning(
                "Falling back to in-memory knowledge storage due to missing dependencies"
            )
        else:
            self.logger.info(f"Loading embedding model: {self.config.embedding_model}")
            self.embedding_model = SentenceTransformer(self.config.embedding_model)
            self.embedding_dim = (
                self.embedding_model.get_sentence_embedding_dimension()
            )
            self.client = QdrantClient(
                host=self.config.vector_db_host,
                port=self.config.vector_db_port
            )
            self._ensure_collection()

        self.logger.info("Vector Knowledge Manager initialized")
    
    def _ensure_collection(self) -> None:
        """Ensure the knowledge collection exists."""
        if self._using_memory_backend:
            return

        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]

            if self.config.vector_db_collection not in collection_names:
                self.logger.info(
                    f"Creating collection: {self.config.vector_db_collection}"
                )
                self.client.create_collection(
                    collection_name=self.config.vector_db_collection,
                    vectors_config=VectorParams(
                        size=self.embedding_dim,
                        distance=Distance.COSINE
                    )
                )
        except Exception as e:
            self.logger.error(f"Error ensuring collection exists: {e}")
            raise
    
    def add_knowledge(
        self,
        content: str,
        category: str,
        source: str,
        confidence: float = 1.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Optional[str]:
        """
        Add a knowledge entry to the vector database.
        
        Args:
            content: Knowledge content
            category: Category of knowledge
            source: Source component
            confidence: Confidence score (0-1)
            metadata: Additional metadata
            
        Returns:
            Knowledge ID if successful, None otherwise
        """
        try:
            embedding = self._encode_text(content)
            
            # Create knowledge entry
            knowledge_id = str(uuid.uuid4())
            timestamp = datetime.now().isoformat()
            
            payload = {
                "content": content,
                "category": category,
                "source": source,
                "confidence": confidence,
                "timestamp": timestamp,
                "usage_count": 0,
                "last_accessed": timestamp,
                **(metadata or {})
            }
            
            if self._using_memory_backend:
                self._memory_store[knowledge_id] = {
                    "id": knowledge_id,
                    "vector": embedding,
                    "payload": payload,
                }
            else:
                self.client.upsert(
                    collection_name=self.config.vector_db_collection,
                    points=[
                        PointStruct(
                            id=knowledge_id,
                            vector=embedding,
                            payload=payload
                        )
                    ]
                )
            
            self.logger.info(
                f"Added knowledge entry: {knowledge_id} - {category} from {source}"
            )
            return knowledge_id
            
        except Exception as e:
            self.logger.error(f"Error adding knowledge: {e}")
            return None
    
    def search_knowledge(
        self,
        query: str,
        category: Optional[str] = None,
        source: Optional[str] = None,
        limit: int = 5,
        min_confidence: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Search for relevant knowledge using semantic similarity.
        
        Args:
            query: Search query
            category: Filter by category
            source: Filter by source
            limit: Maximum number of results
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of knowledge entries with similarity scores
        """
        try:
            query_embedding = self._encode_text(query)

            if self._using_memory_backend:
                return self._search_memory(
                    query_embedding,
                    category,
                    source,
                    limit,
                    min_confidence,
                )
            
            # Build filter conditions
            filter_conditions = []
            
            if category:
                filter_conditions.append(
                    FieldCondition(
                        key="category",
                        match=MatchValue(value=category)
                    )
                )
            
            if source:
                filter_conditions.append(
                    FieldCondition(
                        key="source",
                        match=MatchValue(value=source)
                    )
                )
            
            if min_confidence > 0:
                filter_conditions.append(
                    FieldCondition(
                        key="confidence",
                        range={
                            "gte": min_confidence
                        }
                    )
                )
            
            query_filter = Filter(must=filter_conditions) if filter_conditions else None
            
            # Search vector database
            results = self.client.search(
                collection_name=self.config.vector_db_collection,
                query_vector=query_embedding,
                query_filter=query_filter,
                limit=limit
            )
            
            # Update usage counts
            for result in results:
                self._update_usage(result.id)
            
            # Format results
            knowledge_entries = []
            for result in results:
                entry = {
                    "id": result.id,
                    "score": result.score,
                    **result.payload
                }
                knowledge_entries.append(entry)
            
            self.logger.debug(
                f"Found {len(knowledge_entries)} knowledge entries for query: {query}"
            )
            return knowledge_entries
            
        except Exception as e:
            self.logger.error(f"Error searching knowledge: {e}")
            return []
    
    def _update_usage(self, knowledge_id: str) -> None:
        """
        Update usage statistics for a knowledge entry.

        Args:
            knowledge_id: ID of the knowledge entry
        """
        if self._using_memory_backend:
            entry = self._memory_store.get(knowledge_id)
            if not entry:
                return

            payload = entry["payload"]
            payload["usage_count"] = payload.get("usage_count", 0) + 1
            payload["last_accessed"] = datetime.now().isoformat()
            return

        try:
            result = self.client.retrieve(
                collection_name=self.config.vector_db_collection,
                ids=[knowledge_id]
            )

            if not result:
                return

            entry = result[0]
            payload = entry.payload

            payload["usage_count"] = payload.get("usage_count", 0) + 1
            payload["last_accessed"] = datetime.now().isoformat()

            self.client.set_payload(
                collection_name=self.config.vector_db_collection,
                payload=payload,
                points=[knowledge_id]
            )

        except Exception as e:
            self.logger.error(f"Error updating usage for {knowledge_id}: {e}")

    def _encode_text(self, text: str) -> List[float]:
        if self.embedding_model:
            return self.embedding_model.encode(text).tolist()
        return self._simple_embedding(text)

    def _simple_embedding(self, text: str) -> List[float]:
        vector = [0.0] * self.embedding_dim
        for idx, byte in enumerate(text.encode("utf-8")):
            vector[idx % self.embedding_dim] += byte / 255.0

        norm = math.sqrt(sum(value * value for value in vector)) or 1.0
        return [value / norm for value in vector]

    def _cosine_similarity(self, vector_a: List[float], vector_b: List[float]) -> float:
        numerator = sum(a * b for a, b in zip(vector_a, vector_b))
        denominator = math.sqrt(sum(a * a for a in vector_a)) * math.sqrt(
            sum(b * b for b in vector_b)
        )
        if denominator == 0:
            return 0.0
        return numerator / denominator

    def _search_memory(
        self,
        query_embedding: List[float],
        category: Optional[str],
        source: Optional[str],
        limit: int,
        min_confidence: float,
    ) -> List[Dict[str, Any]]:
        matches: List[Tuple[float, Dict[str, Any]]] = []

        for entry in self._memory_store.values():
            payload = entry["payload"]
            if category and payload.get("category") != category:
                continue
            if source and payload.get("source") != source:
                continue
            if payload.get("confidence", 0.0) < min_confidence:
                continue

            score = self._cosine_similarity(query_embedding, entry["vector"])
            matches.append((score, entry))

        matches.sort(key=lambda item: item[0], reverse=True)

        results = []
        for score, entry in matches[:limit]:
            self._update_usage(entry["id"])
            record = {
                "id": entry["id"],
                "score": score,
                **entry["payload"],
            }
            results.append(record)

        return results
    
    def get_knowledge_by_id(self, knowledge_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific knowledge entry by ID.
        
        Args:
            knowledge_id: ID of the knowledge entry
            
        Returns:
            Knowledge entry, or None if not found
        """
        try:
            result = self.client.retrieve(
                collection_name=self.config.vector_db_collection,
                ids=[knowledge_id]
            )
            
            if not result:
                return None
            
            entry = result[0]
            return {
                "id": entry.id,
                **entry.payload
            }
            
        except Exception as e:
            self.logger.error(f"Error retrieving knowledge {knowledge_id}: {e}")
            return None
    
    def update_knowledge(
        self,
        knowledge_id: str,
        confidence: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update an existing knowledge entry.
        
        Args:
            knowledge_id: ID of the knowledge entry
            confidence: New confidence score
            metadata: Additional metadata to merge
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Retrieve current entry
            result = self.client.retrieve(
                collection_name=self.config.vector_db_collection,
                ids=[knowledge_id]
            )
            
            if not result:
                self.logger.warning(f"Knowledge entry not found: {knowledge_id}")
                return False
            
            entry = result[0]
            payload = entry.payload
            
            # Update fields
            if confidence is not None:
                payload["confidence"] = confidence
            
            if metadata:
                payload.update(metadata)
            
            # Update in database
            self.client.set_payload(
                collection_name=self.config.vector_db_collection,
                payload=payload,
                points=[knowledge_id]
            )
            
            self.logger.info(f"Updated knowledge entry: {knowledge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating knowledge {knowledge_id}: {e}")
            return False
    
    def delete_knowledge(self, knowledge_id: str) -> bool:
        """
        Delete a knowledge entry.
        
        Args:
            knowledge_id: ID of the knowledge entry
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.config.vector_db_collection,
                points_selector=[knowledge_id]
            )
            
            self.logger.info(f"Deleted knowledge entry: {knowledge_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error deleting knowledge {knowledge_id}: {e}")
            return False
    
    def cleanup_old_knowledge(self, days: Optional[int] = None) -> int:
        """
        Delete knowledge entries older than specified days.
        
        Args:
            days: Number of days to retain (uses config default if None)
            
        Returns:
            Number of entries deleted
        """
        try:
            retention_days = days or self.config.knowledge_retention_days
            cutoff_date = datetime.now() - timedelta(days=retention_days)
            cutoff_iso = cutoff_date.isoformat()
            
            # Scroll through all points to find old ones
            # Note: Qdrant doesn't support direct date filtering in delete,
            # so we need to retrieve and delete manually
            offset = None
            deleted_count = 0
            batch_size = 100
            
            while True:
                results, offset = self.client.scroll(
                    collection_name=self.config.vector_db_collection,
                    limit=batch_size,
                    offset=offset
                )
                
                if not results:
                    break
                
                old_ids = [
                    r.id for r in results
                    if r.payload.get("timestamp", "") < cutoff_iso
                ]
                
                if old_ids:
                    self.client.delete(
                        collection_name=self.config.vector_db_collection,
                        points_selector=old_ids
                    )
                    deleted_count += len(old_ids)
                
                if offset is None:
                    break
            
            self.logger.info(
                f"Cleaned up {deleted_count} old knowledge entries "
                f"(older than {retention_days} days)"
            )
            return deleted_count
            
        except Exception as e:
            self.logger.error(f"Error cleaning up old knowledge: {e}")
            return 0
    
    def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the knowledge base.
        
        Returns:
            Dictionary with knowledge base statistics
        """
        try:
            collection_info = self.client.get_collection(
                collection_name=self.config.vector_db_collection
            )
            
            # Get category distribution
            category_counts = {}
            offset = None
            batch_size = 100
            
            while True:
                results, offset = self.client.scroll(
                    collection_name=self.config.vector_db_collection,
                    limit=batch_size,
                    offset=offset
                )
                
                if not results:
                    break
                
                for r in results:
                    category = r.payload.get("category", "unknown")
                    category_counts[category] = category_counts.get(category, 0) + 1
                
                if offset is None:
                    break
            
            return {
                "total_entries": collection_info.points_count,
                "vector_dimension": collection_info.config.params.vectors.size,
                "category_distribution": category_counts
            }
            
        except Exception as e:
            self.logger.error(f"Error getting knowledge stats: {e}")
            return {}

