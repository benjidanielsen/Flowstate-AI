#!/usr/bin/env python3
"""
Coordination Helpers for FlowState-AI
Provides safe, atomic operations for coordination file updates
Prevents JSON corruption from concurrent access
"""

import json
import fcntl
import time
from pathlib import Path
from typing import Dict, Any, Callable, Optional
import contextlib

class CoordinationFileManager:
    """
    Thread-safe and process-safe coordination file manager
    Uses file locking to prevent corruption from concurrent access
    """
    
    def __init__(self, coordination_file: str = ".manus-coordination/coordination-status.json"):
        self.project_root = Path(__file__).parent
        self.coordination_file = self.project_root / coordination_file
        self.lock_file = self.coordination_file.with_suffix('.lock')
        
    @contextlib.contextmanager
    def _file_lock(self, timeout: int = 10):
        """
        Acquire an exclusive file lock with timeout
        
        Args:
            timeout: Maximum seconds to wait for lock
        """
        lock_fd = None
        try:
            # Create lock file if it doesn't exist
            self.lock_file.touch(exist_ok=True)
            lock_fd = open(self.lock_file, 'w')
            
            # Try to acquire lock with timeout
            start_time = time.time()
            while True:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                    break
                except IOError:
                    if time.time() - start_time > timeout:
                        raise TimeoutError(f"Could not acquire lock after {timeout} seconds")
                    time.sleep(0.1)
            
            yield lock_fd
            
        finally:
            if lock_fd:
                try:
                    fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
                    lock_fd.close()
                except:
                    pass
    
    def read_coordination_file(self) -> Dict[str, Any]:
        """
        Safely read coordination file with locking
        
        Returns:
            Dictionary containing coordination data
        """
        with self._file_lock():
            if not self.coordination_file.exists():
                return self._create_empty_coordination_file()
            
            try:
                with open(self.coordination_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                print(f"⚠️  Coordination file corrupted, creating backup and new file")
                # Backup corrupted file
                backup_path = self.coordination_file.with_suffix('.json.corrupted')
                self.coordination_file.rename(backup_path)
                return self._create_empty_coordination_file()
    
    def write_coordination_file(self, data: Dict[str, Any]) -> None:
        """
        Safely write coordination file with locking and atomic write
        
        Args:
            data: Dictionary to write to coordination file
        """
        with self._file_lock():
            # Write to temporary file first (atomic operation)
            temp_file = self.coordination_file.with_suffix('.tmp')
            
            try:
                with open(temp_file, 'w') as f:
                    json.dump(data, f, indent=2)
                
                # Atomic rename
                temp_file.replace(self.coordination_file)
                
            except Exception as e:
                # Clean up temp file on error
                if temp_file.exists():
                    temp_file.unlink()
                raise e
    
    def update_coordination_file(self, update_func: Callable[[Dict[str, Any]], Dict[str, Any]]) -> Dict[str, Any]:
        """
        Safely update coordination file using a function
        Handles read-modify-write atomically
        
        Args:
            update_func: Function that takes current data and returns updated data
            
        Returns:
            Updated coordination data
        """
        with self._file_lock():
            # Read current data (without locking again)
            if not self.coordination_file.exists():
                current_data = self._create_empty_coordination_file_unlocked()
            else:
                try:
                    with open(self.coordination_file, 'r') as f:
                        current_data = json.load(f)
                except json.JSONDecodeError:
                    print(f"⚠️  Coordination file corrupted, creating backup and new file")
                    backup_path = self.coordination_file.with_suffix('.json.corrupted')
                    self.coordination_file.rename(backup_path)
                    current_data = self._create_empty_coordination_file_unlocked()
            
            # Apply update function
            updated_data = update_func(current_data)
            
            # Write back atomically (without locking again)
            temp_file = self.coordination_file.with_suffix('.tmp')
            try:
                with open(temp_file, 'w') as f:
                    json.dump(updated_data, f, indent=2)
                temp_file.replace(self.coordination_file)
            except Exception as e:
                if temp_file.exists():
                    temp_file.unlink()
                raise e
            
            return updated_data
    
    def update_manus_status(self, manus_id: str, status_updates: Dict[str, Any]) -> None:
        """
        Update a specific Manus instance's status
        
        Args:
            manus_id: ID of the Manus instance (e.g., "manus_1")
            status_updates: Dictionary of fields to update
        """
        def update_func(data: Dict[str, Any]) -> Dict[str, Any]:
            if manus_id not in data:
                data[manus_id] = {}
            
            # Update specified fields
            for key, value in status_updates.items():
                data[manus_id][key] = value
            
            # Always update timestamp
            from datetime import datetime
            data[manus_id]['last_update'] = datetime.utcnow().isoformat() + 'Z'
            
            return data
        
        self.update_coordination_file(update_func)
    
    def send_message(self, from_manus: str, to_manus: str, message: str) -> None:
        """
        Send a message from one Manus to another
        
        Args:
            from_manus: Sender Manus ID
            to_manus: Recipient Manus ID
            message: Message content
        """
        def update_func(data: Dict[str, Any]) -> Dict[str, Any]:
            if from_manus not in data:
                data[from_manus] = {}
            
            message_key = f"message_to_{to_manus}"
            data[from_manus][message_key] = message
            
            # Update timestamp
            from datetime import datetime
            data[from_manus]['last_update'] = datetime.utcnow().isoformat() + 'Z'
            
            return data
        
        self.update_coordination_file(update_func)
    
    def get_messages_for_manus(self, manus_id: str) -> Dict[str, str]:
        """
        Get all messages addressed to a specific Manus
        
        Args:
            manus_id: ID of the Manus instance
            
        Returns:
            Dictionary mapping sender IDs to messages
        """
        data = self.read_coordination_file()
        messages = {}
        
        message_key = f"message_to_{manus_id}"
        
        for sender_id, sender_data in data.items():
            if isinstance(sender_data, dict) and message_key in sender_data:
                messages[sender_id] = sender_data[message_key]
        
        return messages
    
    def _create_empty_coordination_file(self) -> Dict[str, Any]:
        """Create an empty coordination file structure"""
        empty_data = {
            "coordination_version": "1.0",
            "last_global_update": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        self.write_coordination_file(empty_data)
        return empty_data
    
    def _create_empty_coordination_file_unlocked(self) -> Dict[str, Any]:
        """Create an empty coordination file structure without acquiring lock"""
        empty_data = {
            "coordination_version": "1.0",
            "last_global_update": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        # Write directly without locking (caller already has lock)
        temp_file = self.coordination_file.with_suffix('.tmp')
        with open(temp_file, 'w') as f:
            json.dump(empty_data, f, indent=2)
        temp_file.replace(self.coordination_file)
        return empty_data


# Convenience functions for common operations

def update_my_status(manus_id: str, status: str, current_task: str, **kwargs):
    """
    Quick function to update current Manus status
    
    Args:
        manus_id: Your Manus ID
        status: Current status string
        current_task: Description of current task
        **kwargs: Additional fields to update
    """
    manager = CoordinationFileManager()
    
    updates = {
        "status": status,
        "current_task": current_task,
        **kwargs
    }
    
    manager.update_manus_status(manus_id, updates)


def send_message_to_manus(from_manus: str, to_manus: str, message: str):
    """
    Quick function to send a message to another Manus
    
    Args:
        from_manus: Your Manus ID
        to_manus: Recipient Manus ID
        message: Message content
    """
    manager = CoordinationFileManager()
    manager.send_message(from_manus, to_manus, message)


def get_my_messages(manus_id: str) -> Dict[str, str]:
    """
    Quick function to get messages for current Manus
    
    Args:
        manus_id: Your Manus ID
        
    Returns:
        Dictionary mapping sender IDs to messages
    """
    manager = CoordinationFileManager()
    return manager.get_messages_for_manus(manus_id)


# Example usage
if __name__ == "__main__":
    # Test the coordination helpers
    print("Testing Coordination Helpers...")
    
    # Update status
    update_my_status(
        "manus_test",
        status="ACTIVE - TESTING",
        current_task="Testing coordination helpers",
        progress="50%"
    )
    print("✅ Status updated")
    
    # Send a message
    send_message_to_manus(
        "manus_test",
        "manus_2",
        "Testing message system"
    )
    print("✅ Message sent")
    
    # Read messages
    messages = get_my_messages("manus_2")
    print(f"✅ Messages for manus_2: {messages}")
    
    print("\n✅ All tests passed!")
