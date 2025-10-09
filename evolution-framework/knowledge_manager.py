"""
Vector Knowledge Management - Semantic storage and retrieval system

This module implements vector-based knowledge management using FAISS for
efficient similarity search and semantic understanding of system knowledge.
"""

import asyncio
import json
import logging
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)


@dataclass
class KnowledgeEntry:
    """Represents a single knowledge entry"""
    entry_id: str
    content: str
    metadata: Dict[str, Any]
    embedding: Optional[np.ndarray] = None
    category: str = "general"
    source: str = "unknown"
    confidence: float = 1.0
    created_at: str = None
    updated_at: str = None
    access_count: int = 0
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow().isoformat()
        if self.updated_at is None:
            self.updated_at = self.created_at
    
    def to_dict(self) -> Dict:
        """Convert to dictionary (excluding embedding for serialization)"""
        data = asdict(self)
        data.pop("embedding", None)
        return data


class VectorKnowledgeManager:
    """
    Vector-based knowledge management system
    
    Uses sentence transformers for embeddings and FAISS for efficient
    similarity search across stored knowledge.
    """
    
    def __init__(
        self,
        embedding_model: str = "all-MiniLM-L6-v2",
        index_type: str = "Flat",
        storage_path: Optional[str] = None
    ):
        """
        Initialize Vector Knowledge Manager
        
        Args:
            embedding_model: Name of sentence-transformers model to use
            index_type: FAISS index type ("Flat", "IVFFlat", "HNSW")
            storage_path: Path to persist knowledge base
        """
        self.embedding_model_name = embedding_model
        self.index_type = index_type
        self.storage_path = Path(storage_path) if storage_path else Path("./knowledge_base")
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize components
        self.model = None
        self.index = None
        self.entries: Dict[str, KnowledgeEntry] = {}
        self.entry_ids: List[str] = []  # Maintains order for FAISS index
        
        # Lazy initialization flags
        self._initialized = False
        
        logger.info(f"Vector Knowledge Manager created with model={embedding_model}, "
                   f"index_type={index_type}")
    
    async def initialize(self) -> None:
        """Initialize embedding model and FAISS index"""
        if self._initialized:
            return
        
        try:
            # Import here to avoid loading at module import time
            from sentence_transformers import SentenceTransformer
            import faiss
            
            logger.info(f"Loading embedding model: {self.embedding_model_name}")
            self.model = SentenceTransformer(self.embedding_model_name)
            
            # Get embedding dimension
            test_embedding = self.model.encode(["test"])
            embedding_dim = test_embedding.shape[1]
            
            # Initialize FAISS index
            logger.info(f"Initializing FAISS index: {self.index_type} (dim={embedding_dim})")
            
            if self.index_type == "Flat":
                self.index = faiss.IndexFlatL2(embedding_dim)
            elif self.index_type == "IVFFlat":
                quantizer = faiss.IndexFlatL2(embedding_dim)
                self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
            elif self.index_type == "HNSW":
                self.index = faiss.IndexHNSWFlat(embedding_dim, 32)
            else:
                raise ValueError(f"Unsupported index type: {self.index_type}")
            
            # Load existing knowledge base if available
            await self._load_knowledge_base()
            
            self._initialized = True
            logger.info("Vector Knowledge Manager initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Vector Knowledge Manager: {str(e)}", exc_info=True)
            raise
    
    async def add_knowledge(
        self,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        category: str = "general",
        source: str = "manual",
        confidence: float = 1.0
    ) -> str:
        """
        Add new knowledge entry
        
        Args:
            content: Text content of the knowledge
            metadata: Additional metadata
            category: Knowledge category
            source: Source of the knowledge
            confidence: Confidence score (0-1)
            
        Returns:
            Entry ID
        """
        if not self._initialized:
            await self.initialize()
        
        # Generate entry ID
        entry_id = f"{category}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Generate embedding
        embedding = self.model.encode([content])[0]
        
        # Create entry
        entry = KnowledgeEntry(
            entry_id=entry_id,
            content=content,
            metadata=metadata or {},
            embedding=embedding,
            category=category,
            source=source,
            confidence=confidence
        )
        
        # Store entry
        self.entries[entry_id] = entry
        self.entry_ids.append(entry_id)
        
        # Add to FAISS index
        self.index.add(np.array([embedding]))
        
        logger.info(f"Added knowledge entry: {entry_id} (category={category})")
        
        # Persist
        await self._save_knowledge_base()
        
        return entry_id
    
    async def search_knowledge(
        self,
        query: str,
        top_k: int = 5,
        category_filter: Optional[str] = None,
        min_confidence: float = 0.0
    ) -> List[Tuple[KnowledgeEntry, float]]:
        """
        Search for relevant knowledge
        
        Args:
            query: Search query
            top_k: Number of results to return
            category_filter: Filter by category
            min_confidence: Minimum confidence threshold
            
        Returns:
            List of (entry, similarity_score) tuples
        """
        if not self._initialized:
            await self.initialize()
        
        if len(self.entries) == 0:
            return []
        
        # Generate query embedding
        query_embedding = self.model.encode([query])[0]
        
        # Search in FAISS
        distances, indices = self.index.search(np.array([query_embedding]), top_k * 2)
        
        # Filter and rank results
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx < 0 or idx >= len(self.entry_ids):
                continue
            
            entry_id = self.entry_ids[idx]
            entry = self.entries[entry_id]
            
            # Apply filters
            if category_filter and entry.category != category_filter:
                continue
            if entry.confidence < min_confidence:
                continue
            
            # Convert L2 distance to similarity score (0-1)
            similarity = 1.0 / (1.0 + dist)
            
            results.append((entry, similarity))
            
            # Update access count
            entry.access_count += 1
            
            if len(results) >= top_k:
                break
        
        logger.info(f"Knowledge search: query='{query[:50]}...', results={len(results)}")
        
        return results
    
    async def update_knowledge(
        self,
        entry_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        confidence: Optional[float] = None
    ) -> bool:
        """
        Update existing knowledge entry
        
        Args:
            entry_id: ID of entry to update
            content: New content (if changing)
            metadata: New metadata (merged with existing)
            confidence: New confidence score
            
        Returns:
            Success status
        """
        if entry_id not in self.entries:
            logger.warning(f"Entry not found: {entry_id}")
            return False
        
        entry = self.entries[entry_id]
        
        # Update content and re-embed if changed
        if content and content != entry.content:
            entry.content = content
            entry.embedding = self.model.encode([content])[0]
            
            # Update in FAISS index
            idx = self.entry_ids.index(entry_id)
            # Note: FAISS doesn't support in-place updates, so we rebuild
            await self._rebuild_index()
        
        # Update metadata
        if metadata:
            entry.metadata.update(metadata)
        
        # Update confidence
        if confidence is not None:
            entry.confidence = confidence
        
        entry.updated_at = datetime.utcnow().isoformat()
        
        logger.info(f"Updated knowledge entry: {entry_id}")
        
        # Persist
        await self._save_knowledge_base()
        
        return True
    
    async def delete_knowledge(self, entry_id: str) -> bool:
        """
        Delete knowledge entry
        
        Args:
            entry_id: ID of entry to delete
            
        Returns:
            Success status
        """
        if entry_id not in self.entries:
            logger.warning(f"Entry not found: {entry_id}")
            return False
        
        # Remove from entries
        del self.entries[entry_id]
        self.entry_ids.remove(entry_id)
        
        # Rebuild FAISS index
        await self._rebuild_index()
        
        logger.info(f"Deleted knowledge entry: {entry_id}")
        
        # Persist
        await self._save_knowledge_base()
        
        return True
    
    async def get_knowledge_by_category(self, category: str) -> List[KnowledgeEntry]:
        """Get all knowledge entries in a category"""
        return [entry for entry in self.entries.values() if entry.category == category]
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """Get statistics about the knowledge base"""
        if len(self.entries) == 0:
            return {
                "total_entries": 0,
                "categories": {},
                "sources": {},
                "avg_confidence": 0.0
            }
        
        categories = {}
        sources = {}
        total_confidence = 0.0
        
        for entry in self.entries.values():
            categories[entry.category] = categories.get(entry.category, 0) + 1
            sources[entry.source] = sources.get(entry.source, 0) + 1
            total_confidence += entry.confidence
        
        return {
            "total_entries": len(self.entries),
            "categories": categories,
            "sources": sources,
            "avg_confidence": total_confidence / len(self.entries),
            "most_accessed": sorted(
                self.entries.values(),
                key=lambda e: e.access_count,
                reverse=True
            )[:5]
        }
    
    async def _rebuild_index(self) -> None:
        """Rebuild FAISS index from scratch"""
        if len(self.entries) == 0:
            return
        
        # Get all embeddings in order
        embeddings = np.array([
            self.entries[entry_id].embedding
            for entry_id in self.entry_ids
        ])
        
        # Reset index
        embedding_dim = embeddings.shape[1]
        
        if self.index_type == "Flat":
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif self.index_type == "IVFFlat":
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, 100)
            if len(embeddings) >= 100:
                self.index.train(embeddings)
        elif self.index_type == "HNSW":
            self.index = faiss.IndexHNSWFlat(embedding_dim, 32)
        
        # Add all embeddings
        self.index.add(embeddings)
        
        logger.info(f"Rebuilt FAISS index with {len(embeddings)} entries")
    
    async def _save_knowledge_base(self) -> None:
        """Persist knowledge base to disk"""
        try:
            # Save entries (without embeddings to save space)
            entries_file = self.storage_path / "entries.json"
            entries_data = {
                entry_id: entry.to_dict()
                for entry_id, entry in self.entries.items()
            }
            
            with open(entries_file, 'w') as f:
                json.dump(entries_data, f, indent=2)
            
            # Save embeddings separately
            embeddings_file = self.storage_path / "embeddings.pkl"
            embeddings_data = {
                entry_id: entry.embedding
                for entry_id, entry in self.entries.items()
            }
            
            with open(embeddings_file, 'wb') as f:
                pickle.dump(embeddings_data, f)
            
            # Save entry IDs order
            ids_file = self.storage_path / "entry_ids.json"
            with open(ids_file, 'w') as f:
                json.dump(self.entry_ids, f)
            
            # Save FAISS index
            index_file = self.storage_path / "faiss.index"
            import faiss
            faiss.write_index(self.index, str(index_file))
            
            logger.debug(f"Saved knowledge base to {self.storage_path}")
            
        except Exception as e:
            logger.error(f"Failed to save knowledge base: {str(e)}", exc_info=True)
    
    async def _load_knowledge_base(self) -> None:
        """Load knowledge base from disk"""
        try:
            entries_file = self.storage_path / "entries.json"
            embeddings_file = self.storage_path / "embeddings.pkl"
            ids_file = self.storage_path / "entry_ids.json"
            index_file = self.storage_path / "faiss.index"
            
            if not entries_file.exists():
                logger.info("No existing knowledge base found")
                return
            
            # Load entries
            with open(entries_file, 'r') as f:
                entries_data = json.load(f)
            
            # Load embeddings
            with open(embeddings_file, 'rb') as f:
                embeddings_data = pickle.load(f)
            
            # Load entry IDs
            with open(ids_file, 'r') as f:
                self.entry_ids = json.load(f)
            
            # Reconstruct entries
            for entry_id, entry_dict in entries_data.items():
                entry = KnowledgeEntry(**entry_dict)
                entry.embedding = embeddings_data[entry_id]
                self.entries[entry_id] = entry
            
            # Load FAISS index
            import faiss
            self.index = faiss.read_index(str(index_file))
            
            logger.info(f"Loaded knowledge base: {len(self.entries)} entries")
            
        except Exception as e:
            logger.error(f"Failed to load knowledge base: {str(e)}", exc_info=True)

