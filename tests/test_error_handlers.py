"""
Test suite for error handlers in the Flowstate-AI unified dashboard.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from flask import Flask
from error_handlers import register_error_handlers

@pytest.fixture
def app():
    """Create a test Flask app with error handlers."""
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.secret_key = 'test_secret_key'
    register_error_handlers(test_app)
    
    # Create test routes that trigger errors
    @test_app.route('/trigger_400')
    def trigger_400():
        from werkzeug.exceptions import BadRequest
        raise BadRequest("Test bad request")
    
    @test_app.route('/trigger_401')
    def trigger_401():
        from werkzeug.exceptions import Unauthorized
        raise Unauthorized("Test unauthorized")
    
    @test_app.route('/trigger_403')
    def trigger_403():
        from werkzeug.exceptions import Forbidden
        raise Forbidden("Test forbidden")
    
    @test_app.route('/trigger_404')
    def trigger_404():
        from werkzeug.exceptions import NotFound
        raise NotFound("Test not found")
    
    @test_app.route('/trigger_500')
    def trigger_500():
        raise Exception("Test internal server error")
    
    return test_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_400_error_handler(client):
    """Test 400 Bad Request error handler."""
    response = client.get('/trigger_400')
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
    assert 'Bad request' in data['error']
    assert 'check your input' in data['error']

def test_401_error_handler(client):
    """Test 401 Unauthorized error handler."""
    response = client.get('/trigger_401')
    assert response.status_code == 401
    data = response.get_json()
    assert 'error' in data
    assert 'Unauthorized' in data['error']
    assert 'log in' in data['error']

def test_403_error_handler(client):
    """Test 403 Forbidden error handler."""
    response = client.get('/trigger_403')
    assert response.status_code == 403
    data = response.get_json()
    assert 'error' in data
    assert 'Forbidden' in data['error']
    assert 'permission' in data['error']

def test_404_error_handler(client):
    """Test 404 Not Found error handler."""
    response = client.get('/trigger_404')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data
    assert b'Return to Dashboard' in response.data

def test_500_error_handler(client):
    """Test 500 Internal Server Error handler."""
    response = client.get('/trigger_500')
    assert response.status_code == 500
    data = response.get_json()
    assert 'error' in data
    assert 'unexpected error' in data['error'].lower()
    assert 'try again later' in data['error']

def test_nonexistent_route(client):
    """Test 404 for nonexistent routes."""
    response = client.get('/this_route_does_not_exist')
    assert response.status_code == 404
    assert b'404' in response.data
    assert b'Page Not Found' in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
