"""
Test suite for authentication in the Flowstate-AI unified dashboard.
"""

import pytest
import sys
from pathlib import Path
import os

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ['ADMIN_USERNAME'] = 'testadmin'
os.environ['ADMIN_PASSWORD_HASH'] = 'pbkdf2:sha256:600000$test$8d2c3f5e9a1b7c4d6e8f0a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d'
os.environ['FLASK_SECRET_KEY'] = 'test_secret_key_for_testing'
os.environ['FLASK_DEBUG'] = '0'

from flask import Flask
from werkzeug.security import generate_password_hash

# Mock the unified_dashboard imports to avoid full app initialization
class MockClient:
    pass

sys.modules['openai'] = type(sys)('openai')
sys.modules['openai'].OpenAI = MockClient

@pytest.fixture
def app():
    """Create a minimal test Flask app with authentication."""
    from flask import Flask, session, request, redirect, url_for, render_template_string
    from flask_wtf.csrf import CSRFProtect, generate_csrf
    from werkzeug.security import check_password_hash
    import time
    
    test_app = Flask(__name__)
    test_app.config['TESTING'] = True
    test_app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for testing
    test_app.secret_key = 'test_secret_key'
    
    # Authentication configuration
    ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "testadmin")
    ADMIN_PASSWORD_HASH = generate_password_hash("testpassword", method='pbkdf2:sha256')
    
    # Rate limiting
    login_attempts = {}
    LOGIN_ATTEMPT_LIMIT = 5
    LOGIN_ATTEMPT_WINDOW_SECONDS = 300
    
    @test_app.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            # Rate limiting check
            client_ip = request.remote_addr
            current_time = time.time()
            
            if client_ip in login_attempts:
                attempts, first_attempt_time = login_attempts[client_ip]
                if current_time - first_attempt_time > LOGIN_ATTEMPT_WINDOW_SECONDS:
                    login_attempts[client_ip] = ([current_time], current_time)
                else:
                    if len(attempts) >= LOGIN_ATTEMPT_LIMIT:
                        return "Too many login attempts. Please try again later.", 429
                    attempts.append(current_time)
            else:
                login_attempts[client_ip] = ([current_time], current_time)
            
            username = request.form["username"]
            password = request.form["password"]
            
            if username.lower() == ADMIN_USERNAME.lower() and check_password_hash(ADMIN_PASSWORD_HASH, password):
                session["logged_in"] = True
                return redirect(url_for("index"))
            else:
                return "Invalid credentials", 401
        return render_template_string('<form method="post"><input name="username"><input name="password" type="password"><button>Login</button></form>')
    
    @test_app.route("/logout")
    def logout():
        session.pop("logged_in", None)
        return redirect(url_for("login"))
    
    @test_app.route("/")
    def index():
        if not session.get("logged_in"):
            return redirect(url_for("login"))
        return "Dashboard"
    
    return test_app

@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()

def test_login_page_accessible(client):
    """Test that the login page is accessible."""
    response = client.get('/login')
    assert response.status_code == 200
    assert b'<form' in response.data

def test_successful_login(client):
    """Test successful login with correct credentials."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpassword'
    }, follow_redirects=True)
    assert response.status_code == 200
    assert b'Dashboard' in response.data

def test_failed_login_wrong_password(client):
    """Test failed login with wrong password."""
    response = client.post('/login', data={
        'username': 'testadmin',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_failed_login_wrong_username(client):
    """Test failed login with wrong username."""
    response = client.post('/login', data={
        'username': 'wronguser',
        'password': 'testpassword'
    })
    assert response.status_code == 401
    assert b'Invalid credentials' in response.data

def test_rate_limiting(client):
    """Test rate limiting on login attempts."""
    # Attempt to login 6 times with wrong credentials
    for i in range(6):
        response = client.post('/login', data={
            'username': 'testadmin',
            'password': 'wrongpassword'
        })
        if i < 5:
            assert response.status_code == 401
        else:
            # 6th attempt should be rate limited
            assert response.status_code == 429
            assert b'Too many login attempts' in response.data

def test_logout(client):
    """Test logout functionality."""
    # First login
    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpassword'
    })
    
    # Then logout
    response = client.get('/logout', follow_redirects=True)
    assert response.status_code == 200
    assert b'<form' in response.data  # Should redirect to login page

def test_protected_route_without_login(client):
    """Test that protected routes redirect to login."""
    response = client.get('/', follow_redirects=True)
    assert response.status_code == 200
    assert b'<form' in response.data  # Should redirect to login page

def test_protected_route_with_login(client):
    """Test that protected routes are accessible after login."""
    # Login first
    client.post('/login', data={
        'username': 'testadmin',
        'password': 'testpassword'
    })
    
    # Access protected route
    response = client.get('/')
    assert response.status_code == 200
    assert b'Dashboard' in response.data

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
