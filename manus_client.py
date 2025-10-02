#!/usr/bin/env python3.11
"""
MANUS CLIENT LIBRARY
Easy-to-use client for Manus instances to communicate with coordination API
"""

import requests
import json
import time
import threading
from datetime import datetime
from pathlib import Path
import socketio as sio

class ManusClient:
    """Client for Manus instances to interact with coordination system"""
    
    def __init__(self, manus_id, role="worker", capabilities=None, api_url="http://localhost:5000"):
        self.manus_id = manus_id
        self.role = role
        self.capabilities = capabilities or []
        self.api_url = api_url
        self.current_task = None
        self.registered = False
        self.running = False
        
        # WebSocket client
        self.sio = sio.Client()
        self.setup_websocket()
        
        # Coordination directory
        self.coord_dir = Path("/home/ubuntu/Flowstate-AI/.manus-coordination")
        self.coord_dir.mkdir(parents=True, exist_ok=True)
        
        # Callbacks
        self.on_task_assigned_callback = None
        self.on_message_callback = None
        self.on_command_callback = None
    
    def setup_websocket(self):
        """Setup WebSocket event handlers"""
        
        @self.sio.on('connected')
        def on_connected(data):
            print(f"✅ {self.manus_id}: Connected to coordination API")
        
        @self.sio.on('task_assigned')
        def on_task_assigned(data):
            if data.get('manus_id') == self.manus_id:
                print(f"📋 {self.manus_id}: Task assigned - {data.get('task_id')}")
                if self.on_task_assigned_callback:
                    self.on_task_assigned_callback(data)
        
        @self.sio.on('message_received')
        def on_message(data):
            if data.get('to') == self.manus_id or data.get('to') == 'all':
                print(f"💬 {self.manus_id}: Message from {data.get('from')}")
                if self.on_message_callback:
                    self.on_message_callback(data)
        
        @self.sio.on('command_received')
        def on_command(data):
            if data.get('to') == self.manus_id:
                print(f"⚡ {self.manus_id}: Command received - {data.get('command', {}).get('command')}")
                if self.on_command_callback:
                    self.on_command_callback(data.get('command'))
        
        @self.sio.on('broadcast')
        def on_broadcast(data):
            print(f"📢 {self.manus_id}: Broadcast from {data.get('from')}")
            if self.on_message_callback:
                self.on_message_callback(data)
    
    def register(self):
        """Register with coordination API"""
        try:
            response = requests.post(
                f"{self.api_url}/api/register",
                json={
                    'manus_id': self.manus_id,
                    'role': self.role,
                    'capabilities': self.capabilities,
                    'sandbox_id': f"sandbox-{self.manus_id}"
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.registered = True
                print(f"✅ {self.manus_id}: Registered successfully")
                
                # Connect WebSocket
                try:
                    self.sio.connect(self.api_url)
                except Exception as e:
                    print(f"⚠️  {self.manus_id}: WebSocket connection failed: {e}")
                
                return True
            else:
                print(f"❌ {self.manus_id}: Registration failed - {response.text}")
                return False
        except Exception as e:
            print(f"❌ {self.manus_id}: Registration error - {e}")
            return False
    
    def send_heartbeat(self, status="active", progress=0):
        """Send heartbeat to coordination API"""
        try:
            response = requests.post(
                f"{self.api_url}/api/heartbeat",
                json={
                    'manus_id': self.manus_id,
                    'status': {'status': status},
                    'current_task': self.current_task,
                    'progress': progress
                },
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            print(f"❌ {self.manus_id}: Heartbeat failed - {e}")
            return False
    
    def get_available_tasks(self):
        """Get available tasks"""
        try:
            response = requests.get(
                f"{self.api_url}/api/tasks",
                params={'manus_id': self.manus_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('tasks', [])
            return []
        except Exception as e:
            print(f"❌ {self.manus_id}: Failed to get tasks - {e}")
            return []
    
    def claim_task(self, task_id):
        """Claim a task"""
        try:
            response = requests.post(
                f"{self.api_url}/api/tasks/claim",
                json={
                    'manus_id': self.manus_id,
                    'task_id': task_id
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.current_task = task_id
                print(f"✅ {self.manus_id}: Claimed task {task_id}")
                return True
            else:
                print(f"❌ {self.manus_id}: Failed to claim task {task_id}")
                return False
        except Exception as e:
            print(f"❌ {self.manus_id}: Claim task error - {e}")
            return False
    
    def complete_task(self, task_id, time_taken=None, files_changed=None):
        """Mark task as complete"""
        try:
            response = requests.post(
                f"{self.api_url}/api/tasks/complete",
                json={
                    'manus_id': self.manus_id,
                    'task_id': task_id,
                    'time_taken': time_taken,
                    'files_changed': files_changed or []
                },
                timeout=10
            )
            
            if response.status_code == 200:
                self.current_task = None
                print(f"✅ {self.manus_id}: Completed task {task_id}")
                return True
            else:
                print(f"❌ {self.manus_id}: Failed to complete task {task_id}")
                return False
        except Exception as e:
            print(f"❌ {self.manus_id}: Complete task error - {e}")
            return False
    
    def send_message(self, to, message, subject="", message_type="info", priority="normal"):
        """Send message to another Manus"""
        try:
            response = requests.post(
                f"{self.api_url}/api/messages/send",
                json={
                    'from': self.manus_id,
                    'to': to,
                    'type': message_type,
                    'subject': subject,
                    'message': message,
                    'priority': priority
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print(f"✅ {self.manus_id}: Message sent to {to}")
                return True
            return False
        except Exception as e:
            print(f"❌ {self.manus_id}: Send message error - {e}")
            return False
    
    def get_messages(self):
        """Get messages for this Manus"""
        try:
            response = requests.get(
                f"{self.api_url}/api/messages",
                params={'manus_id': self.manus_id},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('messages', [])
            return []
        except Exception as e:
            print(f"❌ {self.manus_id}: Failed to get messages - {e}")
            return []
    
    def get_status(self):
        """Get overall system status"""
        try:
            response = requests.get(f"{self.api_url}/api/status", timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except Exception as e:
            print(f"❌ {self.manus_id}: Failed to get status - {e}")
            return None

    def send_command(self, to, command, payload=None):
        """Send a command to another Manus"""
        try:
            response = requests.post(
                f"{self.api_url}/api/commands/send",
                json={
                    'from': self.manus_id,
                    'to': to,
                    'command': command,
                    'payload': payload or {}
                },
                timeout=10
            )
            if response.status_code == 200:
                print(f"✅ {self.manus_id}: Command '{command}' sent to {to}")
                return True
            else:
                print(f"❌ {self.manus_id}: Failed to send command '{command}' - {response.text}")
                return False
        except Exception as e:
            print(f"❌ {self.manus_id}: Send command error - {e}")
            return False
    
    def start_heartbeat_thread(self, interval=30):
        """Start background thread for heartbeat"""
        def heartbeat_loop():
            while self.running:
                self.send_heartbeat()
                time.sleep(interval)
        
        self.running = True
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()
        print(f"✅ {self.manus_id}: Heartbeat thread started (interval: {interval}s)")
    
    def stop(self):
        """Stop the client"""
        self.running = False
        if self.sio.connected:
            self.sio.disconnect()
        print(f"✅ {self.manus_id}: Stopped")
    
    def on_task_assigned(self, callback):
        """Register callback for task assignment"""
        self.on_task_assigned_callback = callback
    
    def on_message(self, callback):
        """Register callback for messages"""
        self.on_message_callback = callback
    
    def on_command(self, callback):
        """Register callback for commands"""
        self.on_command_callback = callback
    
    # ============================================================================
    # HIGH-LEVEL WORKFLOW METHODS
    # ============================================================================
    
    def continuous_work_cycle(self, work_function, idle_function=None):
        """
        Implement continuous work cycle
        
        Args:
            work_function: Function to call when working on a task (receives task dict)
            idle_function: Function to call when idle (no task assigned)
        """
        print(f"🔄 {self.manus_id}: Starting continuous work cycle")
        
        last_task_check = 0
        
        while self.running:
            try:
                # Check for new tasks every 2 minutes
                if time.time() - last_task_check > 120:
                    if not self.current_task:
                        tasks = self.get_available_tasks()
                        if tasks:
                            # Claim first available task
                            task = tasks[0]
                            if self.claim_task(task['id']):
                                # Work on task
                                work_function(task)
                    last_task_check = time.time()
                
                # If idle, do idle work
                if not self.current_task and idle_function:
                    idle_function()
                
                # Small sleep to prevent busy loop
                time.sleep(1)
                
            except KeyboardInterrupt:
                print(f"\n⚠️  {self.manus_id}: Interrupted by user")
                break
            except Exception as e:
                print(f"❌ {self.manus_id}: Error in work cycle - {e}")
                time.sleep(5)
        
        print(f"✅ {self.manus_id}: Work cycle stopped")


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

if __name__ == '__main__':
    # Example: Create a Manus client
    client = ManusClient(
        manus_id="manus_test",
        role="test_worker",
        capabilities=["testing", "example"]
    )
    
    # Register
    if client.register():
        # Start heartbeat
        client.start_heartbeat_thread(interval=30)
        
        # Define work function
        def do_work(task):
            print(f"🔨 Working on task: {task['title']}")
            time.sleep(5)  # Simulate work
            client.complete_task(task['id'], time_taken="5s")
        
        # Define idle function
        def do_idle():
            print(f"💤 Idle - reading documentation...")
            time.sleep(10)
        
        # Start continuous work cycle
        try:
            client.continuous_work_cycle(
                work_function=do_work,
                idle_function=do_idle
            )
        except KeyboardInterrupt:
            print("\n⚠️  Stopping...")
        finally:
            client.stop()
