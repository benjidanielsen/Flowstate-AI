from datetime import datetime
from typing import Optional, List, Dict

# In-memory store for demo purposes
class ConversionTracker:
    def __init__(self):
        # Store leads keyed by lead_id
        self.leads = {}
        # Store conversion events keyed by lead_id
        self.conversions = {}

    def track_lead(self, lead_id: str, source: Optional[str] = None, metadata: Optional[Dict] = None):
        """
        Register a new lead.
        """
        if lead_id in self.leads:
            # Lead already tracked
            return
        self.leads[lead_id] = {
            'lead_id': lead_id,
            'source': source,
            'metadata': metadata or {},
            'created_at': datetime.utcnow()
        }

    def track_conversion(self, lead_id: str, customer_id: Optional[str] = None, value: Optional[float] = None):
        """
        Record a conversion event for a lead.
        """
        if lead_id not in self.leads:
            raise ValueError(f"Lead {lead_id} not found")

        self.conversions[lead_id] = {
            'lead_id': lead_id,
            'customer_id': customer_id,
            'value': value,
            'converted_at': datetime.utcnow()
        }

    def get_conversion_rate(self) -> float:
        """
        Returns the conversion rate as a float between 0 and 1.
        """
        total_leads = len(self.leads)
        if total_leads == 0:
            return 0.0
        total_converted = len(self.conversions)
        return total_converted / total_leads

    def get_report(self) -> Dict:
        """
        Returns a summary report containing:
        - total leads
        - total conversions
        - conversion rate
        - conversions detail list
        """
        total_leads = len(self.leads)
        total_conversions = len(self.conversions)
        conversion_rate = self.get_conversion_rate()

        conversions_list = []
        for lead_id, conversion in self.conversions.items():
            lead = self.leads.get(lead_id, {})
            conversions_list.append({
                'lead_id': lead_id,
                'source': lead.get('source'),
                'customer_id': conversion.get('customer_id'),
                'value': conversion.get('value'),
                'converted_at': conversion.get('converted_at').isoformat() if conversion.get('converted_at') else None
            })

        return {
            'total_leads': total_leads,
            'total_conversions': total_conversions,
            'conversion_rate': conversion_rate,
            'conversions': conversions_list
        }

# Singleton instance
tracker = ConversionTracker()

# Example API functions for integration

def register_lead(lead_id: str, source: Optional[str] = None, metadata: Optional[Dict] = None):
    tracker.track_lead(lead_id, source, metadata)


def register_conversion(lead_id: str, customer_id: Optional[str] = None, value: Optional[float] = None):
    tracker.track_conversion(lead_id, customer_id, value)


def get_conversion_report() -> Dict:
    return tracker.get_report()
