"""
Comprehensive test suite for CRM modules (contact service, deal service, email automation, CRM agent)
"""

import unittest
import sys
import os
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from backend.crm_contact_service import CRMContactService
from backend.crm_deal_service import CRMDealService
from backend.crm_email_automation import CRMEmailAutomation


class TestCRMContactService(unittest.TestCase):
    """Test cases for CRMContactService"""
    
    def setUp(self):
        """Set up test fixtures"""
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.service = CRMContactService(redis_client)
        # Clear any existing test data
        test_keys = self.service.redis.keys("crm:contact:test*")
        if test_keys:
            self.service.redis.delete(*test_keys)
    
    def test_create_contact(self):
        """Test creating a new contact"""
        contact_data = {
            "name": "Test User",
            "email": "test@example.com",
            "lifecycle_stage": "lead"
        }
        
        contact = self.service.create_contact(contact_data)
        
        self.assertIsNotNone(contact)
        self.assertEqual(contact["name"], "Test User")
        self.assertEqual(contact["email"], "test@example.com")
        self.assertIn("id", contact)
    
    def test_get_contact(self):
        """Test retrieving a contact"""
        # Create a contact first
        contact_data = {"name": "Test User", "email": "test@example.com"}
        created_contact = self.service.create_contact(contact_data)
        
        # Retrieve it
        retrieved_contact = self.service.get_contact(created_contact["id"])
        
        self.assertIsNotNone(retrieved_contact)
        self.assertEqual(retrieved_contact["id"], created_contact["id"])
        self.assertEqual(retrieved_contact["name"], "Test User")
    
    def test_update_contact(self):
        """Test updating a contact"""
        # Create a contact
        contact_data = {"name": "Test User", "email": "test@example.com", "lifecycle_stage": "lead"}
        created_contact = self.service.create_contact(contact_data)
        
        # Update it
        updates = {"lifecycle_stage": "mql"}
        updated_contact = self.service.update_contact(created_contact["id"], updates)
        
        self.assertEqual(updated_contact["lifecycle_stage"], "mql")
    
    def test_list_contacts(self):
        """Test listing contacts"""
        # Create multiple contacts
        self.service.create_contact({"name": "User 1", "email": "user1@example.com", "lifecycle_stage": "lead"})
        self.service.create_contact({"name": "User 2", "email": "user2@example.com", "lifecycle_stage": "mql"})
        
        # List all contacts
        contacts = self.service.list_contacts()
        
        self.assertGreaterEqual(len(contacts), 2)
    
    def test_list_contacts_by_lifecycle_stage(self):
        """Test filtering contacts by lifecycle stage"""
        # Create contacts with different stages
        self.service.create_contact({"name": "Lead User", "email": "lead@example.com", "lifecycle_stage": "lead"})
        self.service.create_contact({"name": "MQL User", "email": "mql@example.com", "lifecycle_stage": "mql"})
        
        # Filter by lifecycle stage
        leads = self.service.list_contacts(lifecycle_stage="lead")
        
        self.assertTrue(all(c["lifecycle_stage"] == "lead" for c in leads))
    
    def test_delete_contact(self):
        """Test deleting a contact"""
        # Create a contact
        contact_data = {"name": "Test User", "email": "test@example.com"}
        created_contact = self.service.create_contact(contact_data)
        
        # Delete it
        result = self.service.delete_contact(created_contact["id"])
        
        self.assertTrue(result)
        
        # Verify it's deleted
        retrieved = self.service.get_contact(created_contact["id"])
        self.assertIsNone(retrieved)


class TestCRMDealService(unittest.TestCase):
    """Test cases for CRMDealService"""
    
    def setUp(self):
        """Set up test fixtures"""
        import redis
        redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
        self.service = CRMDealService(redis_client)
        # Clear any existing test data
        test_keys = self.service.redis.keys("crm:deal:test*")
        if test_keys:
            self.service.redis.delete(*test_keys)
    
    def test_create_deal(self):
        """Test creating a new deal"""
        deal_data = {
            "pipeline": "Sales",
            "stage": "New",
            "product": "Test Product",
            "amount": 1000.0,
            "currency": "USD"
        }
        
        deal = self.service.create_deal(deal_data)
        
        self.assertIsNotNone(deal)
        self.assertEqual(deal["product"], "Test Product")
        self.assertEqual(deal["amount"], 1000.0)
        self.assertIn("id", deal)
    
    def test_get_deal(self):
        """Test retrieving a deal"""
        # Create a deal first
        deal_data = {"pipeline": "Sales", "stage": "New", "product": "Test Product"}
        created_deal = self.service.create_deal(deal_data)
        
        # Retrieve it
        retrieved_deal = self.service.get_deal(created_deal["id"])
        
        self.assertIsNotNone(retrieved_deal)
        self.assertEqual(retrieved_deal["id"], created_deal["id"])
        self.assertEqual(retrieved_deal["product"], "Test Product")
    
    def test_update_deal(self):
        """Test updating a deal"""
        # Create a deal
        deal_data = {"pipeline": "Sales", "stage": "New", "product": "Test Product", "amount": 1000.0}
        created_deal = self.service.create_deal(deal_data)
        
        # Update it
        updates = {"stage": "Qualified", "amount": 1500.0}
        updated_deal = self.service.update_deal(created_deal["id"], updates)
        
        self.assertEqual(updated_deal["stage"], "Qualified")
        self.assertEqual(updated_deal["amount"], 1500.0)
    
    def test_list_deals(self):
        """Test listing deals"""
        # Create multiple deals
        self.service.create_deal({"pipeline": "Sales", "stage": "New", "product": "Product 1"})
        self.service.create_deal({"pipeline": "Sales", "stage": "Qualified", "product": "Product 2"})
        
        # List all deals
        deals = self.service.list_deals()
        
        self.assertGreaterEqual(len(deals), 2)
    
    def test_list_deals_by_stage(self):
        """Test filtering deals by stage"""
        # Create deals with different stages
        self.service.create_deal({"pipeline": "Sales", "stage": "New", "product": "Product 1"})
        self.service.create_deal({"pipeline": "Sales", "stage": "Qualified", "product": "Product 2"})
        
        # Filter by stage (requires pipeline parameter)
        new_deals = self.service.list_deals(pipeline="Sales", stage="New")
        
        self.assertGreater(len(new_deals), 0)
        # Verify all returned deals have the correct stage
        for deal in new_deals:
            self.assertEqual(deal["stage"], "New")
    
    def test_advance_deal_stage(self):
        """Test advancing a deal to the next stage"""
        # Create a deal
        deal_data = {"pipeline": "Sales", "stage": "New", "product": "Test Product"}
        created_deal = self.service.create_deal(deal_data)
        
        # Advance stage
        advanced_deal = self.service.advance_stage(created_deal["id"])
        
        self.assertNotEqual(advanced_deal["stage"], "New")
    
    def test_delete_deal(self):
        """Test deleting a deal"""
        # Create a deal
        deal_data = {"pipeline": "Sales", "stage": "New", "product": "Test Product"}
        created_deal = self.service.create_deal(deal_data)
        
        # Delete it
        result = self.service.delete_deal(created_deal["id"])
        
        self.assertTrue(result)
        
        # Verify it's deleted
        retrieved = self.service.get_deal(created_deal["id"])
        self.assertIsNone(retrieved)


class TestCRMEmailAutomation(unittest.TestCase):
    """Test cases for CRMEmailAutomation"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.automation = CRMEmailAutomation()
    
    @patch('backend.crm_email_automation.OpenAI')
    def test_generate_personalized_email(self, mock_openai):
        """Test generating a personalized email"""
        # Mock OpenAI response
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = json.dumps({
            "subject": "Welcome to Flowstate-AI",
            "body": "Hi John, welcome!"
        })
        mock_openai.return_value.chat.completions.create.return_value = mock_response
        
        contact = {
            "name": "John Doe",
            "email": "john@example.com",
            "country": "USA",
            "lifecycle_stage": "lead"
        }
        
        email = self.automation.generate_personalized_email("welcome_lead", contact)
        
        self.assertIn("subject", email)
        self.assertIn("body", email)
    
    def test_create_email_sequence(self):
        """Test creating an email sequence"""
        contact = {
            "name": "John Doe",
            "email": "john@example.com",
            "lifecycle_stage": "lead"
        }
        
        sequence = self.automation.create_email_sequence(contact, "lead_nurture")
        
        self.assertGreater(len(sequence), 0)
        self.assertTrue(all("template_key" in email for email in sequence))
        self.assertTrue(all("delay_days" in email for email in sequence))
    
    def test_send_email(self):
        """Test email sending (simulated)"""
        result = self.automation.send_email(
            "test@example.com",
            "Test Subject",
            "Test Body"
        )
        
        self.assertTrue(result)


def run_tests():
    """Run all tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCRMContactService))
    suite.addTests(loader.loadTestsFromTestCase(TestCRMDealService))
    suite.addTests(loader.loadTestsFromTestCase(TestCRMEmailAutomation))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 70)
    print("CRM MODULES TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
