"""
CRM Contact Service for Flowstate-AI
Handles CRUD operations for Contact entities in the CRM system.
"""

import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import redis

class CRMContactService:
    """Service for managing CRM contacts."""
    
    def __init__(self, redis_client: redis.Redis):
        """
        Initialize the CRM Contact Service.
        
        Args:
            redis_client: Redis client instance for data storage
        """
        self.redis = redis_client
        self.contact_prefix = "crm:contact:"
        self.contact_index = "crm:contacts:all"
        
    def create_contact(self, contact_data: Dict) -> Dict:
        """
        Create a new contact in the CRM system.
        
        Args:
            contact_data: Dictionary containing contact information
            
        Returns:
            Created contact with generated ID and timestamps
        """
        contact_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        contact = {
            "id": contact_id,
            "external_id": contact_data.get("external_id", ""),
            "name": contact_data.get("name", ""),
            "email": contact_data.get("email", ""),
            "phone": contact_data.get("phone", ""),
            "handle_ig": contact_data.get("handle_ig", ""),
            "country": contact_data.get("country", ""),
            "language": contact_data.get("language", "en"),
            "lifecycle_stage": contact_data.get("lifecycle_stage", "lead"),
            "consent_email": contact_data.get("consent_email", False),
            "consent_sms": contact_data.get("consent_sms", False),
            "consent_messaging": contact_data.get("consent_messaging", False),
            "terms_version": contact_data.get("terms_version", ""),
            "utm_source": contact_data.get("utm_source", ""),
            "utm_medium": contact_data.get("utm_medium", ""),
            "utm_campaign": contact_data.get("utm_campaign", ""),
            "utm_content": contact_data.get("utm_content", ""),
            "utm_term": contact_data.get("utm_term", ""),
            "created_at": timestamp,
            "updated_at": timestamp
        }
        
        # Store contact in Redis
        contact_key = f"{self.contact_prefix}{contact_id}"
        self.redis.set(contact_key, json.dumps(contact))
        
        # Add to index
        self.redis.sadd(self.contact_index, contact_id)
        
        # Index by lifecycle stage
        stage_index = f"crm:contacts:stage:{contact['lifecycle_stage']}"
        self.redis.sadd(stage_index, contact_id)
        
        return contact
    
    def get_contact(self, contact_id: str) -> Optional[Dict]:
        """
        Retrieve a contact by ID.
        
        Args:
            contact_id: UUID of the contact
            
        Returns:
            Contact dictionary or None if not found
        """
        contact_key = f"{self.contact_prefix}{contact_id}"
        contact_data = self.redis.get(contact_key)
        
        if contact_data:
            return json.loads(contact_data)
        return None
    
    def update_contact(self, contact_id: str, updates: Dict) -> Optional[Dict]:
        """
        Update an existing contact.
        
        Args:
            contact_id: UUID of the contact
            updates: Dictionary of fields to update
            
        Returns:
            Updated contact or None if not found
        """
        contact = self.get_contact(contact_id)
        if not contact:
            return None
        
        # Track lifecycle stage change for re-indexing
        old_stage = contact.get("lifecycle_stage")
        
        # Update fields
        for key, value in updates.items():
            if key not in ["id", "created_at"]:  # Prevent updating immutable fields
                contact[key] = value
        
        contact["updated_at"] = datetime.utcnow().isoformat()
        
        # Save updated contact
        contact_key = f"{self.contact_prefix}{contact_id}"
        self.redis.set(contact_key, json.dumps(contact))
        
        # Update stage index if lifecycle_stage changed
        new_stage = contact.get("lifecycle_stage")
        if old_stage != new_stage:
            old_stage_index = f"crm:contacts:stage:{old_stage}"
            new_stage_index = f"crm:contacts:stage:{new_stage}"
            self.redis.srem(old_stage_index, contact_id)
            self.redis.sadd(new_stage_index, contact_id)
        
        return contact
    
    def delete_contact(self, contact_id: str) -> bool:
        """
        Delete a contact.
        
        Args:
            contact_id: UUID of the contact
            
        Returns:
            True if deleted, False if not found
        """
        contact = self.get_contact(contact_id)
        if not contact:
            return False
        
        # Remove from Redis
        contact_key = f"{self.contact_prefix}{contact_id}"
        self.redis.delete(contact_key)
        
        # Remove from indexes
        self.redis.srem(self.contact_index, contact_id)
        stage_index = f"crm:contacts:stage:{contact['lifecycle_stage']}"
        self.redis.srem(stage_index, contact_id)
        
        return True
    
    def list_contacts(self, lifecycle_stage: Optional[str] = None, 
                     limit: int = 100, offset: int = 0) -> List[Dict]:
        """
        List contacts with optional filtering.
        
        Args:
            lifecycle_stage: Filter by lifecycle stage
            limit: Maximum number of contacts to return
            offset: Number of contacts to skip
            
        Returns:
            List of contact dictionaries
        """
        if lifecycle_stage:
            index_key = f"crm:contacts:stage:{lifecycle_stage}"
        else:
            index_key = self.contact_index
        
        # Get contact IDs from index
        contact_ids = list(self.redis.smembers(index_key))
        
        # Apply pagination
        paginated_ids = contact_ids[offset:offset + limit]
        
        # Retrieve contacts
        contacts = []
        for contact_id in paginated_ids:
            contact_id_str = contact_id.decode('utf-8') if isinstance(contact_id, bytes) else contact_id
            contact = self.get_contact(contact_id_str)
            if contact:
                contacts.append(contact)
        
        return contacts
    
    def get_contact_count(self, lifecycle_stage: Optional[str] = None) -> int:
        """
        Get the count of contacts.
        
        Args:
            lifecycle_stage: Filter by lifecycle stage
            
        Returns:
            Number of contacts
        """
        if lifecycle_stage:
            index_key = f"crm:contacts:stage:{lifecycle_stage}"
        else:
            index_key = self.contact_index
        
        return self.redis.scard(index_key)
