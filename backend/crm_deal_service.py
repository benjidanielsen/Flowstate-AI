"""
CRM Deal Service for Flowstate-AI
Handles CRUD operations for Deal entities in the CRM system.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import redis

class CRMDealService:
    """Service for managing CRM deals."""
    
    # Pipeline stages configuration
    PIPELINE_STAGES = {
        "Recruiting": ["New", "Qualified", "Booked", "Held", "Joined", "Lost", "No-Show"],
        "Sales": ["New", "Qualified", "Booked", "Held", "Won", "Lost", "No-Show"]
    }
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the CRM Deal Service.
        
        Args:
            redis_client: Redis client instance for data storage
        """
        self.redis = redis_client
        self.deal_prefix = "crm:deal:"
        self.deal_index = "crm:deals:all"
        
    def create_deal(self, deal_data: Dict) -> Dict:
        """
        Create a new deal in the CRM system.
        
        Args:
            deal_data: Dictionary containing deal information
            
        Returns:
            Created deal with generated ID and timestamps
        """
        deal_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        pipeline = deal_data.get("pipeline", "Sales")
        stage = deal_data.get("stage", "New")
        
        # Validate pipeline and stage
        if pipeline not in self.PIPELINE_STAGES:
            raise ValueError(f"Invalid pipeline: {pipeline}")
        if stage not in self.PIPELINE_STAGES[pipeline]:
            raise ValueError(f"Invalid stage '{stage}' for pipeline '{pipeline}'")
        
        deal = {
            "id": deal_id,
            "pipeline": pipeline,
            "stage": stage,
            "amount": deal_data.get("amount", 0.0),
            "currency": deal_data.get("currency", "USD"),
            "contact_id": deal_data.get("contact_id", ""),
            "owner_id": deal_data.get("owner_id", ""),
            "product": deal_data.get("product", ""),
            "booking_time": deal_data.get("booking_time", ""),
            "booking_status": deal_data.get("booking_status", ""),
            "notes": deal_data.get("notes", ""),
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Store deal in Redis
        deal_key = f"{self.deal_prefix}{deal_id}"
        self.redis.set(deal_key, json.dumps(deal))
        
        # Add to indexes
        self.redis.sadd(self.deal_index, deal_id)
        
        # Index by pipeline and stage
        pipeline_index = f"crm:deals:pipeline:{pipeline}"
        stage_index = f"crm:deals:pipeline:{pipeline}:stage:{stage}"
        self.redis.sadd(pipeline_index, deal_id)
        self.redis.sadd(stage_index, deal_id)
        
        # Index by contact
        if deal["contact_id"]:
            contact_index = f"crm:deals:contact:{deal['contact_id']}"
            self.redis.sadd(contact_index, deal_id)
        
        return deal
    
    def get_deal(self, deal_id: str) -> Optional[Dict]:
        """
        Retrieve a deal by ID.
        
        Args:
            deal_id: UUID of the deal
            
        Returns:
            Deal dictionary or None if not found
        """
        deal_key = f"{self.deal_prefix}{deal_id}"
        deal_data = self.redis.get(deal_key)
        
        if deal_data:
            return json.loads(deal_data)
        return None
    
    def update_deal(self, deal_id: str, updates: Dict) -> Optional[Dict]:
        """
        Update an existing deal.
        
        Args:
            deal_id: UUID of the deal
            updates: Dictionary of fields to update
            
        Returns:
            Updated deal or None if not found
        """
        deal = self.get_deal(deal_id)
        if not deal:
            return None
        
        # Track changes for re-indexing
        old_pipeline = deal.get("pipeline")
        old_stage = deal.get("stage")
        old_contact_id = deal.get("contact_id")
        
        # Update fields
        for key, value in updates.items():
            if key not in ["id", "created_at"]:  # Prevent updating immutable fields
                deal[key] = value
        
        # Validate new pipeline and stage if changed
        new_pipeline = deal.get("pipeline")
        new_stage = deal.get("stage")
        if new_pipeline not in self.PIPELINE_STAGES:
            raise ValueError(f"Invalid pipeline: {new_pipeline}")
        if new_stage not in self.PIPELINE_STAGES[new_pipeline]:
            raise ValueError(f"Invalid stage '{new_stage}' for pipeline '{new_pipeline}'")
        
        deal["updated_at"] = datetime.utcnow().isoformat()
        
        # Save updated deal
        deal_key = f"{self.deal_prefix}{deal_id}"
        self.redis.set(deal_key, json.dumps(deal))
        
        # Update indexes if pipeline or stage changed
        if old_pipeline != new_pipeline or old_stage != new_stage:
            old_pipeline_index = f"crm:deals:pipeline:{old_pipeline}"
            old_stage_index = f"crm:deals:pipeline:{old_pipeline}:stage:{old_stage}"
            new_pipeline_index = f"crm:deals:pipeline:{new_pipeline}"
            new_stage_index = f"crm:deals:pipeline:{new_pipeline}:stage:{new_stage}"
            
            self.redis.srem(old_pipeline_index, deal_id)
            self.redis.srem(old_stage_index, deal_id)
            self.redis.sadd(new_pipeline_index, deal_id)
            self.redis.sadd(new_stage_index, deal_id)
        
        # Update contact index if contact changed
        new_contact_id = deal.get("contact_id")
        if old_contact_id != new_contact_id:
            if old_contact_id:
                old_contact_index = f"crm:deals:contact:{old_contact_id}"
                self.redis.srem(old_contact_index, deal_id)
            if new_contact_id:
                new_contact_index = f"crm:deals:contact:{new_contact_id}"
                self.redis.sadd(new_contact_index, deal_id)
        
        return deal
    
    def delete_deal(self, deal_id: str) -> bool:
        """
        Delete a deal.
        
        Args:
            deal_id: UUID of the deal
            
        Returns:
            True if deleted, False if not found
        """
        deal = self.get_deal(deal_id)
        if not deal:
            return False
        
        # Remove from Redis
        deal_key = f"{self.deal_prefix}{deal_id}"
        self.redis.delete(deal_key)
        
        # Remove from indexes
        self.redis.srem(self.deal_index, deal_id)
        
        pipeline_index = f"crm:deals:pipeline:{deal['pipeline']}"
        stage_index = f"crm:deals:pipeline:{deal['pipeline']}:stage:{deal['stage']}"
        self.redis.srem(pipeline_index, deal_id)
        self.redis.srem(stage_index, deal_id)
        
        if deal["contact_id"]:
            contact_index = f"crm:deals:contact:{deal['contact_id']}"
            self.redis.srem(contact_index, deal_id)
        
        return True
    
    def list_deals(self, pipeline: Optional[str] = None, stage: Optional[str] = None,
                   contact_id: Optional[str] = None, limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List deals with optional filtering.
        
        Args:
            pipeline: Filter by pipeline type
            stage: Filter by stage (requires pipeline)
            contact_id: Filter by contact ID
            limit: Maximum number of deals to return
            offset: Number of deals to skip
            
        Returns:
            List of deal dictionaries
        """
        if contact_id:
            index_key = f"crm:deals:contact:{contact_id}"
        elif stage and pipeline:
            index_key = f"crm:deals:pipeline:{pipeline}:stage:{stage}"
        elif pipeline:
            index_key = f"crm:deals:pipeline:{pipeline}"
        else:
            index_key = self.deal_index
        
        # Get deal IDs from index
        deal_ids = list(self.redis.smembers(index_key))
        
        # Apply pagination
        paginated_ids = deal_ids[offset:offset + limit]
        
        # Retrieve deals
        deals = []
        for deal_id in paginated_ids:
            deal_id_str = deal_id.decode('utf-8') if isinstance(deal_id, bytes) else deal_id
            deal = self.get_deal(deal_id_str)
            if deal:
                deals.append(deal)
        
        return deals
    
    def advance_stage(self, deal_id: str) -> Optional[Dict]:
        """
        Advance a deal to the next stage in its pipeline.
        
        Args:
            deal_id: UUID of the deal
            
        Returns:
            Updated deal or None if not found or already at final stage
        """
        deal = self.get_deal(deal_id)
        if not deal:
            return None
        
        pipeline = deal["pipeline"]
        current_stage = deal["stage"]
        stages = self.PIPELINE_STAGES[pipeline]
        
        try:
            current_index = stages.index(current_stage)
            if current_index < len(stages) - 1:
                next_stage = stages[current_index + 1]
                return self.update_deal(deal_id, {"stage": next_stage})
        except ValueError:
            pass
        
        return None
    
    def get_pipeline_stages(self, pipeline: str) -> List[str]:
        """
        Get the list of stages for a specific pipeline.
        
        Args:
            pipeline: Pipeline type
            
        Returns:
            List of stage names
        """
        return self.PIPELINE_STAGES.get(pipeline, [])
    
    def get_deal_count(self, pipeline: Optional[str] = None, stage: Optional[str] = None) -> int:
        """
        Get the count of deals.
        
        Args:
            pipeline: Filter by pipeline type
            stage: Filter by stage (requires pipeline)
            
        Returns:
            Number of deals
        """
        if stage and pipeline:
            index_key = f"crm:deals:pipeline:{pipeline}:stage:{stage}"
        elif pipeline:
            index_key = f"crm:deals:pipeline:{pipeline}"
        else:
            index_key = self.deal_index
        
        return self.redis.scard(index_key)
