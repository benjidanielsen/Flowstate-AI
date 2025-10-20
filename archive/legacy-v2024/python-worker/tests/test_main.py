import pytest
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestHealthEndpoints:
    """Test health and root endpoints"""
    
    def test_root_endpoint(self):
        """Test root endpoint returns correct message"""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Flowstate-AI Python Worker"
        assert "timestamp" in data
    
    def test_health_check_endpoint(self):
        """Test health check endpoint"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data


class TestReminderEndpoints:
    """Test reminder-related endpoints"""
    
    @patch('httpx.AsyncClient')
    def test_create_reminder_success(self, mock_client):
        """Test successful reminder creation"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-reminder-id",
            "customer_id": "test-customer-id",
            "type": "follow_up_24h",
            "message": "Test reminder",
            "scheduled_for": datetime.now().isoformat(),
            "completed": False
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        reminder_data = {
            "customer_id": "test-customer-id",
            "type": "follow_up_24h",
            "message": "Test reminder",
            "scheduled_for": datetime.now().isoformat()
        }
        response = client.post("/reminders", json=reminder_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-reminder-id"
        assert data["customer_id"] == "test-customer-id"
    
    @patch('httpx.AsyncClient')
    def test_get_due_reminders_success(self, mock_client):
        """Test fetching due reminders"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code == 200
        mock_response.json.return_value = [
            {
                "id": "reminder-1",
                "customer_id": "customer-1",
                "type": "follow_up_24h",
                "message": "Test reminder 1",
                "scheduled_for": datetime.now().isoformat(),
                "completed": False
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.get("/reminders/due")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["id"] == "reminder-1"
    
    @patch('httpx.AsyncClient')
    def test_complete_reminder_success(self, mock_client):
        """Test completing a reminder"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "id": "test-reminder-id",
            "customer_id": "test-customer-id",
            "completed": True
        }
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.post("/reminders/test-reminder-id/complete")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "test-reminder-id"
        assert data["completed"] is True
    
    @patch('httpx.AsyncClient')
    def test_complete_reminder_not_found(self, mock_client):
        """Test completing a non-existent reminder"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = None
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.post("/reminders/non-existent-id/complete")
        
        assert response.status_code == 404
    
    @patch('httpx.AsyncClient')
    def test_process_due_reminders_success(self, mock_client):
        """Test processing due reminders"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"reminder_id": "reminder-1", "status": "processed"},
            {"reminder_id": "reminder-2", "status": "processed"}
        ]
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.post("/reminders/process-due")
        
        assert response.status_code == 200
        data = response.json()
        assert "processed" in data
        assert data["processed"] == 2
        assert "results" in data


class TestNBAEndpoints:
    """Test Next Best Action endpoints"""
    
    @patch('httpx.AsyncClient')
    def test_get_nba_without_customer_id(self, mock_client):
        """Test fetching NBA recommendations without customer ID"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "customer_id": "customer-1",
                "customer_name": "Test Customer",
                "action_type": "follow_up_needed",
                "title": "Follow up with Test Customer",
                "priority": 70
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.get("/nba?limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["customer_id"] == "customer-1"
    
    @patch('httpx.AsyncClient')
    def test_get_nba_with_customer_id(self, mock_client):
        """Test fetching NBA recommendations for specific customer"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "customer_id": "customer-1",
                "customer_name": "Test Customer",
                "action_type": "pipeline_action",
                "title": "Initial contact and qualification",
                "priority": 80
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.get("/nba?customer_id=customer-1&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["customer_id"] == "customer-1"
    
    @patch('httpx.AsyncClient')
    def test_analyze_customer_data_success(self, mock_client):
        """Test analyzing customer data and generating NBA recommendations"""
        # Mock the httpx client
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "customer_id": "customer-1",
                "recommendations": ["action-1", "action-2"]
            },
            {
                "customer_id": "customer-2",
                "recommendations": ["action-3"]
            }
        ]
        mock_response.raise_for_status = MagicMock()
        
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(return_value=mock_response)
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.post("/nba/analyze")
        
        assert response.status_code == 200
        data = response.json()
        assert "analyzed" in data
        assert data["analyzed"] == 2
        assert "recommendations" in data


class TestErrorHandling:
    """Test error handling in endpoints"""
    
    @patch('httpx.AsyncClient')
    def test_create_reminder_backend_error(self, mock_client):
        """Test reminder creation when backend returns error"""
        # Mock the httpx client to raise an exception
        mock_client_instance = AsyncMock()
        mock_client_instance.post = AsyncMock(side_effect=Exception("Backend error"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        reminder_data = {
            "customer_id": "test-customer-id",
            "type": "follow_up_24h",
            "message": "Test reminder",
            "scheduled_for": datetime.now().isoformat()
        }
        response = client.post("/reminders", json=reminder_data)
        
        assert response.status_code == 500
    
    @patch('httpx.AsyncClient')
    def test_get_nba_backend_error(self, mock_client):
        """Test NBA fetch when backend returns error"""
        # Mock the httpx client to raise an exception
        mock_client_instance = AsyncMock()
        mock_client_instance.get = AsyncMock(side_effect=Exception("Backend error"))
        mock_client.return_value.__aenter__.return_value = mock_client_instance
        
        # Make request
        response = client.get("/nba?limit=10")
        
        assert response.status_code == 500


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

