import pytest
import sys
import os
import sqlite3
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.reminder_service import ReminderService


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
def reminder_service(test_db_path):
    """Create reminder service with test database"""
    service = ReminderService()
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
         "Make initial contact", datetime.now().isoformat()),
        ("customer-2", "Jane Smith", "jane@example.com", "098-765-4321", "Relationship",
         datetime.now().isoformat(), datetime.now().isoformat(), 
         "Building rapport", "Schedule presentation", datetime.now().isoformat()),
    ]
    
    for customer in customers:
        cursor.execute("""
            INSERT INTO customers (id, name, email, phone, status, created_at, updated_at, notes, next_action, next_action_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, customer)
    
    conn.commit()
    conn.close()


class TestReminderServiceCreate:
    """Test reminder creation"""
    
    @pytest.mark.asyncio
    async def test_create_reminder_success(self, reminder_service, sample_customer_data):
        """Test successful reminder creation"""
        scheduled_time = datetime.now() + timedelta(hours=24)
        
        result = await reminder_service.create_reminder(
            customer_id="customer-1",
            reminder_type="follow_up_24h",
            message="Test reminder message",
            scheduled_for=scheduled_time
        )
        
        assert result is not None
        assert "id" in result
        assert result["customer_id"] == "customer-1"
        assert result["type"] == "follow_up_24h"
        assert result["message"] == "Test reminder message"
        assert result["completed"] is False
    
    @pytest.mark.asyncio
    async def test_create_reminder_persists_to_database(self, reminder_service, sample_customer_data, test_db_path):
        """Test that created reminder is persisted to database"""
        scheduled_time = datetime.now() + timedelta(hours=24)
        
        result = await reminder_service.create_reminder(
            customer_id="customer-1",
            reminder_type="follow_up_24h",
            message="Test reminder message",
            scheduled_for=scheduled_time
        )
        
        # Verify in database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (result["id"],))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[1] == "customer-1"  # customer_id
        assert row[2] == "follow_up_24h"  # type
        assert row[3] == "Test reminder message"  # message


class TestReminderServiceGetDue:
    """Test fetching due reminders"""
    
    @pytest.mark.asyncio
    async def test_get_due_reminders_returns_due_reminders(self, reminder_service, sample_customer_data, test_db_path):
        """Test fetching due reminders"""
        # Insert due and future reminders
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        future_time = (datetime.now() + timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-due", "customer-1", "follow_up_24h", "Due reminder", 
              due_time, 0, datetime.now().isoformat()))
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-future", "customer-2", "follow_up_48h", "Future reminder", 
              future_time, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        due_reminders = await reminder_service.get_due_reminders()
        
        assert len(due_reminders) > 0
        due_ids = [r["id"] for r in due_reminders]
        assert "reminder-due" in due_ids
        assert "reminder-future" not in due_ids
    
    @pytest.mark.asyncio
    async def test_get_due_reminders_excludes_completed(self, reminder_service, sample_customer_data, test_db_path):
        """Test that completed reminders are not returned"""
        # Insert completed due reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-completed", "customer-1", "follow_up_24h", "Completed reminder", 
              due_time, 1, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        due_reminders = await reminder_service.get_due_reminders()
        
        due_ids = [r["id"] for r in due_reminders]
        assert "reminder-completed" not in due_ids
    
    @pytest.mark.asyncio
    async def test_get_due_reminders_includes_customer_info(self, reminder_service, sample_customer_data, test_db_path):
        """Test that due reminders include customer information"""
        # Insert due reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-due", "customer-1", "follow_up_24h", "Due reminder", 
              due_time, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        due_reminders = await reminder_service.get_due_reminders()
        
        assert len(due_reminders) > 0
        reminder = due_reminders[0]
        assert "customer_name" in reminder
        assert "customer_email" in reminder
        assert "customer_phone" in reminder
        assert reminder["customer_name"] == "John Doe"


class TestReminderServiceComplete:
    """Test completing reminders"""
    
    @pytest.mark.asyncio
    async def test_complete_reminder_success(self, reminder_service, sample_customer_data, test_db_path):
        """Test successfully completing a reminder"""
        # Insert reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-1", "customer-1", "follow_up_24h", "Test reminder", 
              datetime.now().isoformat(), 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        result = await reminder_service.complete_reminder("reminder-1")
        
        assert result is not None
        assert result["id"] == "reminder-1"
        assert result["completed"] is True
    
    @pytest.mark.asyncio
    async def test_complete_reminder_persists_to_database(self, reminder_service, sample_customer_data, test_db_path):
        """Test that completion is persisted to database"""
        # Insert reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-1", "customer-1", "follow_up_24h", "Test reminder", 
              datetime.now().isoformat(), 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        await reminder_service.complete_reminder("reminder-1")
        
        # Verify in database
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT completed FROM reminders WHERE id = ?", ("reminder-1",))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[0] == 1  # completed
    
    @pytest.mark.asyncio
    async def test_complete_reminder_nonexistent(self, reminder_service, sample_customer_data):
        """Test completing a non-existent reminder"""
        result = await reminder_service.complete_reminder("nonexistent-reminder")
        
        assert result is None


class TestReminderServiceProcessDue:
    """Test processing due reminders"""
    
    @pytest.mark.asyncio
    async def test_process_due_reminders_completes_reminders(self, reminder_service, sample_customer_data, test_db_path):
        """Test that processing due reminders marks them as complete"""
        # Insert due reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-due", "customer-1", "follow_up_24h", "Due reminder", 
              due_time, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        results = await reminder_service.process_due_reminders()
        
        # Verify reminder is completed
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT completed FROM reminders WHERE id = ?", ("reminder-due",))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        assert row[0] == 1  # completed
    
    @pytest.mark.asyncio
    async def test_process_due_reminders_creates_follow_ups(self, reminder_service, sample_customer_data, test_db_path):
        """Test that processing creates follow-up reminders"""
        # Insert due reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-due", "customer-1", "follow_up_24h", "Due reminder", 
              due_time, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        results = await reminder_service.process_due_reminders()
        
        assert len(results) > 0
        assert "follow_up" in results[0]
    
    @pytest.mark.asyncio
    async def test_process_due_reminders_creates_interactions(self, reminder_service, sample_customer_data, test_db_path):
        """Test that processing creates interaction records"""
        # Insert due reminder
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        due_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ("reminder-due", "customer-1", "follow_up_24h", "Due reminder", 
              due_time, 0, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        await reminder_service.process_due_reminders()
        
        # Verify interaction was created
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interactions WHERE customer_id = ? AND type = ?", 
                      ("customer-1", "reminder"))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None


class TestReminderServiceAutomatedReminders:
    """Test automated reminder creation"""
    
    @pytest.mark.asyncio
    async def test_create_automated_reminders_lead(self, reminder_service, sample_customer_data, test_db_path):
        """Test creating automated reminders for Lead status"""
        await reminder_service.create_automated_reminders("customer-1", "Lead")
        
        # Verify reminders were created
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE customer_id = ?", ("customer-1",))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) > 0
        # Should have 24h and 48h follow-ups
        types = [row[2] for row in rows]
        assert "follow_up_24h" in types
        assert "follow_up_48h" in types
    
    @pytest.mark.asyncio
    async def test_create_automated_reminders_qualified(self, reminder_service, sample_customer_data, test_db_path):
        """Test creating automated reminders for Qualified status"""
        await reminder_service.create_automated_reminders("customer-1", "Qualified")
        
        # Verify reminders were created
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE customer_id = ?", ("customer-1",))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) > 0
        # Should have 2h and 24h follow-ups
        types = [row[2] for row in rows]
        assert "follow_up_2h" in types
        assert "follow_up_24h" in types
    
    @pytest.mark.asyncio
    async def test_create_automated_reminders_invalid_status(self, reminder_service, sample_customer_data, test_db_path):
        """Test creating automated reminders for invalid status"""
        await reminder_service.create_automated_reminders("customer-1", "InvalidStatus")
        
        # Verify no reminders were created
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM reminders WHERE customer_id = ?", ("customer-1",))
        rows = cursor.fetchall()
        conn.close()
        
        assert len(rows) == 0
    
    @pytest.mark.asyncio
    async def test_create_automated_reminders_correct_timing(self, reminder_service, sample_customer_data, test_db_path):
        """Test that automated reminders have correct timing"""
        await reminder_service.create_automated_reminders("customer-1", "Lead")
        
        # Verify reminder timing
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT type, scheduled_for FROM reminders WHERE customer_id = ? AND type = ?", 
                      ("customer-1", "follow_up_24h"))
        row = cursor.fetchone()
        conn.close()
        
        assert row is not None
        scheduled_time = datetime.fromisoformat(row[1])
        expected_time = datetime.now() + timedelta(hours=24)
        # Allow 1 minute tolerance
        assert abs((scheduled_time - expected_time).total_seconds()) < 60


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

