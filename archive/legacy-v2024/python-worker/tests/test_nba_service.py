import pytest
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.nba_service import NBAService


@pytest.fixture
def test_db_path(tmp_path):
    """Create a temporary database for testing"""
    db_path = tmp_path / "test_flowstate.db"
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create customers table
    cursor.execute("""
        CREATE TABLE customers (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            status TEXT,
            created_at TEXT,
            updated_at TEXT,
            notes TEXT,
            next_action TEXT,
            next_action_date TEXT
        )
    """)
    
    # Create interactions table
    cursor.execute("""
        CREATE TABLE interactions (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            type TEXT,
            content TEXT,
            created_at TEXT,
            completed INTEGER
        )
    """)
    
    # Create reminders table
    cursor.execute("""
        CREATE TABLE reminders (
            id TEXT PRIMARY KEY,
            customer_id TEXT,
            type TEXT,
            message TEXT,
            scheduled_for TEXT,
            completed INTEGER,
            created_at TEXT
        )
    """)
    
    conn.commit()
    conn.close()
    
    return str(db_path)


@pytest.fixture
def nba_service(test_db_path):
    """Create NBA service with test database"""
    service = NBAService()
    service.db_path = test_db_path
    return service


@pytest.fixture
def sample_customer_data(test_db_path):
    """Insert sample customer data for testing"""
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # Insert test customers
    customers = [
        ("customer-1", "John Doe", "john@example.com", "123-456-7890", "Lead", 
         datetime.now().isoformat(), datetime.now().isoformat(), "Test notes", 
         "Make initial contact", (datetime.now() - timedelta(days=2)).isoformat()),
        ("customer-2", "Jane Smith", "jane@example.com", "098-765-4321", "Relationship",
         datetime.now().isoformat(), (datetime.now() - timedelta(days=10)).isoformat(), 
         "Building rapport", "Schedule presentation", datetime.now().isoformat()),
        ("customer-3", "Bob Johnson", "bob@example.com", "555-555-5555", "Qualified",
         datetime.now().isoformat(), (datetime.now() - timedelta(days=5)).isoformat(),
         "Highly interested", "Send materials", (datetime.now() + timedelta(days=1)).isoformat()),
    ]
    
    for customer in customers:
        cursor.execute("""
            INSERT INTO customers (id, name, email, phone, status, created_at, updated_at, notes, next_action, next_action_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customer)
    
    # Insert test interactions
    interactions = [
        ("interaction-1", "customer-1", "email", "Initial contact email", 
         (datetime.now() - timedelta(days=1)).isoformat(), 1),
        ("interaction-2", "customer-2", "call", "Follow-up call", 
         (datetime.now() - timedelta(days=15)).isoformat(), 1),
        ("interaction-3", "customer-3", "meeting", "Qualification meeting",
         (datetime.now() - timedelta(days=3)).isoformat(), 0),
    ]
    
    for interaction in interactions:
        cursor.execute("""
            INSERT INTO interactions (id, customer_id, type, content, created_at, completed)
            VALUES (?, ?, ?, ?, ?, ?)
        """, interaction)
    
    # Insert test reminders
    reminders = [
        ("reminder-1", "customer-1", "follow_up_24h", "Follow up on initial contact",
         (datetime.now() - timedelta(hours=12)).isoformat(), 0, datetime.now().isoformat()),
        ("reminder-2", "customer-2", "follow_up_7d", "Check in with customer",
         datetime.now().isoformat(), 0, datetime.now().isoformat()),
    ]
    
    for reminder in reminders:
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, reminder)
    
    conn.commit()
    conn.close()


class TestNBAServiceCustomerRecommendations:
    """Test customer-specific NBA recommendations"""
    
    @pytest.mark.asyncio
    async def test_get_customer_recommendations_overdue_action(self, nba_service, sample_customer_data):
        """Test recommendations for customer with overdue action"""
        recommendations = await nba_service._get_customer_recommendations("customer-1")
        
        assert len(recommendations) > 0
        # Should include overdue action recommendation
        overdue_recs = [r for r in recommendations if r["action_type"] == "overdue_action"]
        assert len(overdue_recs) > 0
        assert overdue_recs[0]["urgency"] == "critical"
        assert overdue_recs[0]["priority"] == 95
    
    @pytest.mark.asyncio
    async def test_get_customer_recommendations_pipeline_action(self, nba_service, sample_customer_data):
        """Test pipeline-based recommendations"""
        recommendations = await nba_service._get_customer_recommendations("customer-3")
        
        assert len(recommendations) > 0
        # Should include pipeline action recommendation
        pipeline_recs = [r for r in recommendations if r["action_type"] == "pipeline_action"]
        assert len(pipeline_recs) > 0
        assert pipeline_recs[0]["pipeline_status"] == "Qualified"
    
    @pytest.mark.asyncio
    async def test_get_customer_recommendations_no_interactions(self, nba_service, test_db_path):
        """Test recommendations for customer with no interactions"""
        # Add customer with no interactions
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO customers (id, name, email, phone, status, created_at, updated_at, notes, next_action, next_action_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, ("customer-new", "New Customer", "new@example.com", "111-111-1111", "Lead",
              datetime.now().isoformat(), datetime.now().isoformat(), "", "Contact", None))
        conn.commit()
        conn.close()
        
        recommendations = await nba_service._get_customer_recommendations("customer-new")
        
        assert len(recommendations) > 0
        # Should include first contact recommendation
        first_contact_recs = [r for r in recommendations if r["action_type"] == "first_contact"]
        assert len(first_contact_recs) > 0
        assert first_contact_recs[0]["urgency"] == "high"
    
    @pytest.mark.asyncio
    async def test_get_customer_recommendations_incomplete_interactions(self, nba_service, sample_customer_data):
        """Test recommendations for customer with incomplete interactions"""
        recommendations = await nba_service._get_customer_recommendations("customer-3")
        
        # Should include recommendation to complete interactions
        complete_recs = [r for r in recommendations if r["action_type"] == "complete_interaction"]
        assert len(complete_recs) > 0
    
    @pytest.mark.asyncio
    async def test_get_customer_recommendations_nonexistent_customer(self, nba_service, sample_customer_data):
        """Test recommendations for non-existent customer"""
        recommendations = await nba_service._get_customer_recommendations("nonexistent-customer")
        
        assert len(recommendations) == 0


class TestNBAServiceGlobalRecommendations:
    """Test global NBA recommendations"""
    
    @pytest.mark.asyncio
    async def test_get_global_recommendations_overdue_customers(self, nba_service, sample_customer_data):
        """Test global recommendations include overdue customers"""
        recommendations = await nba_service._get_global_recommendations(10)
        
        assert len(recommendations) > 0
        # Should include overdue customer
        overdue_recs = [r for r in recommendations if r["action_type"] == "overdue_next_action"]
        assert len(overdue_recs) > 0
        assert overdue_recs[0]["customer_id"] == "customer-1"
    
    @pytest.mark.asyncio
    async def test_get_global_recommendations_inactive_customers(self, nba_service, sample_customer_data):
        """Test global recommendations include inactive customers"""
        recommendations = await nba_service._get_global_recommendations(10)
        
        # Should include customers without recent interactions
        follow_up_recs = [r for r in recommendations if r["action_type"] == "follow_up_needed"]
        assert len(follow_up_recs) > 0
    
    @pytest.mark.asyncio
    async def test_get_global_recommendations_pipeline_progression(self, nba_service, sample_customer_data):
        """Test global recommendations include pipeline progression candidates"""
        recommendations = await nba_service._get_global_recommendations(10)
        
        # Should include customers ready for next stage
        progression_recs = [r for r in recommendations if r["action_type"] == "pipeline_progression"]
        assert len(progression_recs) > 0
    
    @pytest.mark.asyncio
    async def test_get_global_recommendations_limit(self, nba_service, sample_customer_data):
        """Test global recommendations respect limit parameter"""
        recommendations = await nba_service._get_global_recommendations(2)
        
        assert len(recommendations) <= 2
    
    @pytest.mark.asyncio
    async def test_get_global_recommendations_priority_sorting(self, nba_service, sample_customer_data):
        """Test global recommendations are sorted by priority"""
        recommendations = await nba_service._get_global_recommendations(10)
        
        # Verify recommendations are sorted by priority (descending)
        priorities = [r["priority"] for r in recommendations]
        assert priorities == sorted(priorities, reverse=True)


class TestNBAServiceAnalysisMethods:
    """Test individual analysis methods"""
    
    def test_analyze_pipeline_status_lead(self, nba_service):
        """Test pipeline analysis for Lead status"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead"
        }
        
        recommendations = nba_service._analyze_pipeline_status(customer)
        
        assert len(recommendations) > 0
        assert recommendations[0]["action_type"] == "pipeline_action"
        assert recommendations[0]["priority"] == 80
    
    def test_analyze_pipeline_status_qualified(self, nba_service):
        """Test pipeline analysis for Qualified status"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Qualified"
        }
        
        recommendations = nba_service._analyze_pipeline_status(customer)
        
        assert len(recommendations) > 0
        assert recommendations[0]["priority"] == 90
        assert recommendations[0]["urgency"] == "high"
    
    def test_analyze_interaction_history_no_interactions(self, nba_service):
        """Test interaction analysis with no interactions"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead"
        }
        
        recommendations = nba_service._analyze_interaction_history(customer, [])
        
        assert len(recommendations) > 0
        assert recommendations[0]["action_type"] == "first_contact"
    
    def test_analyze_interaction_history_incomplete_interactions(self, nba_service):
        """Test interaction analysis with incomplete interactions"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead"
        }
        interactions = [
            ("email", "Test content", datetime.now().isoformat(), 0),  # Incomplete
            ("call", "Test content", datetime.now().isoformat(), 1),   # Complete
        ]
        
        recommendations = nba_service._analyze_interaction_history(customer, interactions)
        
        assert len(recommendations) > 0
        complete_recs = [r for r in recommendations if r["action_type"] == "complete_interaction"]
        assert len(complete_recs) > 0
    
    def test_analyze_contact_timing_recent_contact(self, nba_service):
        """Test contact timing analysis with recent contact"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead"
        }
        interactions = [
            ("email", "Test content", datetime.now().isoformat(), 1),
        ]
        
        recommendations = nba_service._analyze_contact_timing(customer, interactions)
        
        # Should not recommend reconnect for recent contact
        assert len(recommendations) == 0
    
    def test_analyze_contact_timing_old_contact(self, nba_service):
        """Test contact timing analysis with old contact"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead"
        }
        interactions = [
            ("email", "Test content", (datetime.now() - timedelta(days=10)).isoformat(), 1),
        ]
        
        recommendations = nba_service._analyze_contact_timing(customer, interactions)
        
        # Should recommend reconnect
        assert len(recommendations) > 0
        assert recommendations[0]["action_type"] == "reconnect"
    
    def test_check_overdue_actions_overdue(self, nba_service):
        """Test overdue action check with overdue action"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead",
            "next_action": "Follow up",
            "next_action_date": (datetime.now() - timedelta(days=3)).isoformat()
        }
        
        recommendations = nba_service._check_overdue_actions(customer)
        
        assert len(recommendations) > 0
        assert recommendations[0]["action_type"] == "overdue_action"
        assert recommendations[0]["urgency"] == "critical"
        assert recommendations[0]["priority"] == 95
    
    def test_check_overdue_actions_not_overdue(self, nba_service):
        """Test overdue action check with future action"""
        customer = {
            "id": "test-customer",
            "name": "Test Customer",
            "status": "Lead",
            "next_action": "Follow up",
            "next_action_date": (datetime.now() + timedelta(days=3)).isoformat()
        }
        
        recommendations = nba_service._check_overdue_actions(customer)
        
        assert len(recommendations) == 0


class TestNBAServiceAnalyzeAndGenerate:
    """Test comprehensive analysis and generation"""
    
    @pytest.mark.asyncio
    async def test_analyze_and_generate_recommendations(self, nba_service, sample_customer_data):
        """Test comprehensive recommendation generation"""
        recommendations = await nba_service.analyze_and_generate_recommendations()
        
        assert len(recommendations) > 0
        # Should include recommendations for all active customers
        customer_ids = set(r["customer_id"] for r in recommendations)
        assert "customer-1" in customer_ids
        assert "customer-2" in customer_ids
        assert "customer-3" in customer_ids
    
    @pytest.mark.asyncio
    async def test_analyze_and_generate_recommendations_sorted(self, nba_service, sample_customer_data):
        """Test that comprehensive recommendations are sorted by priority"""
        recommendations = await nba_service.analyze_and_generate_recommendations()
        
        # Verify recommendations are sorted by priority (descending)
        priorities = [r["priority"] for r in recommendations]
        assert priorities == sorted(priorities, reverse=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

