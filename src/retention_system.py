import datetime
from typing import List, Dict, Optional

class Customer:
    def __init__(self, customer_id: str, email: str):
        self.customer_id = customer_id
        self.email = email
        self.engagement_events: List[Dict] = []
        self.last_engagement: Optional[datetime.datetime] = None
        self.is_active: bool = True

    def log_engagement(self, event_type: str, timestamp: Optional[datetime.datetime] = None):
        if not timestamp:
            timestamp = datetime.datetime.utcnow()
        self.engagement_events.append({"event_type": event_type, "timestamp": timestamp})
        self.last_engagement = timestamp
        self.is_active = True

    def days_since_last_engagement(self) -> Optional[int]:
        if not self.last_engagement:
            return None
        delta = datetime.datetime.utcnow() - self.last_engagement
        return delta.days


class RetentionSystem:
    WINBACK_THRESHOLD_DAYS = 30

    def __init__(self):
        self.customers: Dict[str, Customer] = {}

    def add_customer(self, customer_id: str, email: str):
        if customer_id not in self.customers:
            self.customers[customer_id] = Customer(customer_id, email)

    def log_engagement(self, customer_id: str, event_type: str, timestamp: Optional[datetime.datetime] = None):
        customer = self.customers.get(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        customer.log_engagement(event_type, timestamp)

    def get_inactive_customers(self, days_inactive: int) -> List[Customer]:
        inactive_customers = []
        for customer in self.customers.values():
            days = customer.days_since_last_engagement()
            if days is None or days >= days_inactive:
                inactive_customers.append(customer)
        return inactive_customers

    def generate_winback_campaign(self) -> List[Dict]:
        """
        Returns a list of win-back campaign messages for customers inactive for WINBACK_THRESHOLD_DAYS or more
        """
        inactive_customers = self.get_inactive_customers(self.WINBACK_THRESHOLD_DAYS)
        campaigns = []
        for customer in inactive_customers:
            campaign = {
                "customer_id": customer.customer_id,
                "email": customer.email,
                "subject": "We miss you at Flowstate-AI!",
                "message": (
                    f"Hi there! We've noticed you haven't engaged with Flowstate-AI for a while. "
                    "Come back and check out our latest features – we have something special waiting for you!"
                )
            }
            campaigns.append(campaign)
        return campaigns


# Example usage (would be in a different module or test):
# retention = RetentionSystem()
# retention.add_customer("cust123", "customer@example.com")
# retention.log_engagement("cust123", "login")
# campaigns = retention.generate_winback_campaign()
# for campaign in campaigns:
#     print(campaign)
