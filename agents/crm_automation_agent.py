"""
CRM Automation Agent for Flowstate-AI
Autonomous agent for managing CRM operations, lead qualification, and pipeline automation.
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
import requests
from openai import OpenAI
from pathlib import Path

class CRMAutomationAgent:
    """AI Agent for automating CRM operations."""
    
    def __init__(self, api_base_url: str = "http://localhost:5001/api/v1"):
        """
        Initialize the CRM Automation Agent.
        
        Args:
            api_base_url: Base URL for the CRM API
        """
        self.api_base = api_base_url
        self.client = OpenAI()
        self.agent_name = "CRM Automation Agent"
        self.log_file = Path(__file__).parent.parent / "logs" / "crm_automation_agent.log"
        
    def log(self, message: str):
        """Log agent activity."""
        timestamp = datetime.utcnow().isoformat()
        log_entry = f"[{timestamp}] {self.agent_name}: {message}\n"
        print(log_entry.strip())
        
        try:
            with open(self.log_file, "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Warning: Could not write to log file: {e}")
    
    def get_contacts(self, lifecycle_stage: Optional[str] = None) -> List[Dict]:
        """Fetch contacts from the CRM API."""
        try:
            params = {}
            if lifecycle_stage:
                params["lifecycle_stage"] = lifecycle_stage
            
            response = requests.get(f"{self.api_base}/contacts", params=params)
            response.raise_for_status()
            return response.json().get("contacts", [])
        except Exception as e:
            self.log(f"Error fetching contacts: {e}")
            return []
    
    def get_deals(self, pipeline: Optional[str] = None, stage: Optional[str] = None) -> List[Dict]:
        """Fetch deals from the CRM API."""
        try:
            params = {}
            if pipeline:
                params["pipeline"] = pipeline
            if stage:
                params["stage"] = stage
            
            response = requests.get(f"{self.api_base}/deals", params=params)
            response.raise_for_status()
            return response.json().get("deals", [])
        except Exception as e:
            self.log(f"Error fetching deals: {e}")
            return []
    
    def create_contact(self, contact_data: Dict) -> Optional[Dict]:
        """Create a new contact."""
        try:
            response = requests.post(f"{self.api_base}/contacts", json=contact_data)
            response.raise_for_status()
            contact = response.json()
            self.log(f"Created new contact: {contact['name']} ({contact['id']})")
            return contact
        except Exception as e:
            self.log(f"Error creating contact: {e}")
            return None
    
    def update_contact(self, contact_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing contact."""
        try:
            response = requests.put(f"{self.api_base}/contacts/{contact_id}", json=updates)
            response.raise_for_status()
            contact = response.json()
            self.log(f"Updated contact: {contact_id}")
            return contact
        except Exception as e:
            self.log(f"Error updating contact: {e}")
            return None
    
    def create_deal(self, deal_data: Dict) -> Optional[Dict]:
        """Create a new deal."""
        try:
            response = requests.post(f"{self.api_base}/deals", json=deal_data)
            response.raise_for_status()
            deal = response.json()
            self.log(f"Created new deal: {deal['product']} ({deal['id']})")
            return deal
        except Exception as e:
            self.log(f"Error creating deal: {e}")
            return None
    
    def update_deal(self, deal_id: str, updates: Dict) -> Optional[Dict]:
        """Update an existing deal."""
        try:
            response = requests.put(f"{self.api_base}/deals/{deal_id}", json=updates)
            response.raise_for_status()
            deal = response.json()
            self.log(f"Updated deal: {deal_id}")
            return deal
        except Exception as e:
            self.log(f"Error updating deal: {e}")
            return None
    
    def advance_deal_stage(self, deal_id: str) -> Optional[Dict]:
        """Advance a deal to the next stage."""
        try:
            response = requests.post(f"{self.api_base}/deals/{deal_id}/advance_stage")
            response.raise_for_status()
            deal = response.json()
            self.log(f"Advanced deal {deal_id} to stage: {deal['stage']}")
            return deal
        except Exception as e:
            self.log(f"Error advancing deal stage: {e}")
            return None
    
    def qualify_lead(self, contact: Dict) -> str:
        """
        Use AI to qualify a lead based on contact information.
        
        Returns:
            Qualification level: 'mql' (Marketing Qualified Lead) or 'sql' (Sales Qualified Lead)
        """
        try:
            prompt = f"""
            Analyze the following contact information and determine if this is a Marketing Qualified Lead (MQL) or Sales Qualified Lead (SQL).
            
            Contact Information:
            - Name: {contact.get('name')}
            - Email: {contact.get('email')}
            - Country: {contact.get('country')}
            - UTM Source: {contact.get('utm_source')}
            - UTM Campaign: {contact.get('utm_campaign')}
            
            Criteria:
            - MQL: Shows interest but needs nurturing (e.g., from general campaigns, no specific product interest)
            - SQL: Ready for sales engagement (e.g., from targeted campaigns, high-value country, professional email)
            
            Respond with only 'mql' or 'sql'.
            """
            
            response = self.client.chat.completions.create(
                model="gpt-4.1-mini",
                messages=[
                    {"role": "system", "content": "You are a CRM lead qualification expert."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=10
            )
            
            qualification = response.choices[0].message.content.strip().lower()
            self.log(f"Qualified contact {contact['id']} as: {qualification}")
            return qualification if qualification in ['mql', 'sql'] else 'mql'
        except Exception as e:
            self.log(f"Error qualifying lead: {e}")
            return 'mql'
    
    def process_new_leads(self):
        """Process and qualify new leads."""
        self.log("Starting lead qualification process...")
        
        # Get all leads
        leads = self.get_contacts(lifecycle_stage="lead")
        self.log(f"Found {len(leads)} leads to process")
        
        for lead in leads:
            # Qualify the lead
            qualification = self.qualify_lead(lead)
            
            # Update lifecycle stage
            self.update_contact(lead['id'], {"lifecycle_stage": qualification})
            
            # Create a deal if SQL
            if qualification == 'sql':
                deal_data = {
                    "pipeline": "Sales",
                    "stage": "New",
                    "contact_id": lead['id'],
                    "product": "Flowstate-AI Services",
                    "amount": 0.0,
                    "currency": "USD"
                }
                self.create_deal(deal_data)
        
        self.log("Lead qualification process completed")
    
    def monitor_deals(self):
        """Monitor deals and suggest next actions."""
        self.log("Starting deal monitoring...")
        
        # Get all deals in 'New' stage
        new_deals = self.get_deals(stage="New")
        self.log(f"Found {len(new_deals)} new deals to monitor")
        
        for deal in new_deals:
            # Simulate checking if deal should be advanced
            # In a real scenario, this would check for specific conditions
            # For now, we just log the deal
            self.log(f"Monitoring deal {deal['id']}: {deal['product']} - {deal['stage']}")
        
        self.log("Deal monitoring completed")
    
    def run_automation_cycle(self):
        """Run a full automation cycle."""
        self.log("=" * 50)
        self.log("Starting CRM automation cycle")
        self.log("=" * 50)
        
        # Process new leads
        self.process_new_leads()
        
        # Monitor deals
        self.monitor_deals()
        
        self.log("=" * 50)
        self.log("CRM automation cycle completed")
        self.log("=" * 50)

def main():
    """Main function to run the CRM automation agent."""
    agent = CRMAutomationAgent()
    
    # Run automation cycle
    agent.run_automation_cycle()
    
    # In production, this would run continuously with a scheduler
    # For now, it runs once

if __name__ == "__main__":
    main()
