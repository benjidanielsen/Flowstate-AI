#!/usr/bin/env python3
"""
🔐 AUTHENTICATION SYSTEM
⚡ Handles admin authentication and user management
🎯 Mission: Secure access control for admin dashboard
"""

import sqlite3
import hashlib
import secrets
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('AuthSystem')

PROJECT_ROOT = Path(__file__).parent.parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

class AuthSystem:
    """Handles authentication and authorization"""
    
    def __init__(self):
        self.db_path = DB_PATH
        self._ensure_admin_exists()
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _ensure_admin_exists(self):
        """Ensure the admin user exists"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check if admin exists
        cursor.execute("SELECT COUNT(*) FROM admin_users WHERE LOWER(username) = 'benjidanielsen'")
        count = cursor.fetchone()[0]
        
        if count == 0:
            # Create admin user
            password_hash = self._hash_password('Sagemaster123')
            cursor.execute('''
                INSERT INTO admin_users (username, password_hash)
                VALUES (?, ?)
            ''', ('benjidanielsen', password_hash))
            conn.commit()
            logger.info("✅ Admin user 'benjidanielsen' created")
        
        conn.close()
    
    def authenticate_admin(self, username: str, password: str) -> bool:
        """
        Authenticate admin user
        Username is case-insensitive, password is case-sensitive
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get user with case-insensitive username
        cursor.execute('''
            SELECT password_hash FROM admin_users 
            WHERE LOWER(username) = LOWER(?)
        ''', (username,))
        
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            logger.warning(f"❌ Login attempt with unknown username: {username}")
            return False
        
        stored_hash = result[0]
        provided_hash = self._hash_password(password)
        
        if stored_hash == provided_hash:
            logger.info(f"✅ Admin '{username}' logged in successfully")
            return True
        else:
            logger.warning(f"❌ Failed login attempt for admin '{username}' - incorrect password")
            return False
    
    def create_session_token(self, username: str) -> str:
        """Create a session token for authenticated user"""
        return secrets.token_urlsafe(32)
    
    def change_admin_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change admin password"""
        if not self.authenticate_admin(username, old_password):
            return False
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_hash = self._hash_password(new_password)
        cursor.execute('''
            UPDATE admin_users 
            SET password_hash = ?
            WHERE LOWER(username) = LOWER(?)
        ''', (new_hash, username))
        
        conn.commit()
        conn.close()
        
        logger.info(f"✅ Password changed for admin '{username}'")
        return True

if __name__ == "__main__":
    print("🔐 Authentication System")
    print("=" * 60)
    
    auth = AuthSystem()
    
    print("\n✅ Admin user initialized")
    print("   Username: benjidanielsen (case-insensitive)")
    print("   Password: Sagemaster123 (case-sensitive)")
    
    print("\n🧪 Testing authentication...")
    
    # Test cases
    tests = [
        ("benjidanielsen", "Sagemaster123", True),
        ("BENJIDANIELSEN", "Sagemaster123", True),
        ("BenjiDanielsen", "Sagemaster123", True),
        ("benjidanielsen", "sagemaster123", False),
        ("benjidanielsen", "Sagemaster124", False),
        ("wronguser", "Sagemaster123", False),
    ]
    
    for username, password, expected in tests:
        result = auth.authenticate_admin(username, password)
        status = "✅" if result == expected else "❌"
        print(f"  {status} {username} / {password}: {result}")
    
    print("\n✅ Authentication system operational!")
