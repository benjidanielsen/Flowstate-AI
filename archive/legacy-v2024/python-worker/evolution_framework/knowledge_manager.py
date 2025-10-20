"""
Vector Knowledge Manager

Manages persistent knowledge storage using vector embeddings for semantic search.
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
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
        
        # Initialize embedding model
        self.logger.info(f"Loading embedding model: {self.config.embedding_model}")
        self.embedding_model = SentenceTransformer(self.config.embedding_model)
        self.embedding_dim = self.embedding_model.get_sentence_embedding_dimension()
        
        # Initialize vector database client
        self.client = QdrantClient(
            host=self.config.vector_db_host,
            port=self.config.vector_db_port
        )
        
        # Ensure collection exists
        self._ensure_collection()
        
        self.logger.info("Vector Knowledge Manager initialized")
    
    def _ensure_collection(self) -> None:
        """Ensure the knowledge collection exists."""
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
            # Generate embedding
            embedding = self.embedding_model.encode(content).tolist()
            
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
            
            # Store in vector database
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
            # Generate query embedding
            query_embedding = self.embedding_model.encode(query).tolist()
            
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
        try:
            # Retrieve current entry
            result = self.client.retrieve(
                collection_name=self.config.vector_db_collection,
                ids=[knowledge_id]
            )
            
            if not result:
                return
            
            entry = result[0]
            payload = entry.payload
            
            # Update usage statistics
            payload["usage_count"] = payload.get("usage_count", 0) + 1
            payload["last_accessed"] = datetime.now().isoformat()
            
            # Update in database
            self.client.set_payload(
                collection_name=self.config.vector_db_collection,
                payload=payload,
                points=[knowledge_id]
            )
            
        except Exception as e:
            self.logger.error(f"Error updating usage for {knowledge_id}: {e}")
    
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

