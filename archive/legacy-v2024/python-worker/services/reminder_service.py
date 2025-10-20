import sqlite3
import uuid
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import os

class ReminderService:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_URL', '../data/flowstate.db')
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    async def create_reminder(self, customer_id: str, reminder_type: str, message: str, scheduled_for: datetime):
        """Create a new reminder"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        reminder_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO reminders (id, customer_id, type, message, scheduled_for, completed, created_at)
            VALUES (?, ?, ?, ?, ?, 0, ?)
        """, (reminder_id, customer_id, reminder_type, message, scheduled_for.isoformat(), datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return {
            "id": reminder_id,
            "customer_id": customer_id,
            "type": reminder_type,
            "message": message,
            "scheduled_for": scheduled_for.isoformat(),
            "completed": False
        }
    
    async def get_due_reminders(self) -> List[Dict[str, Any]]:
        """Get all reminders that are due"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute("""
            SELECT r.*, c.name as customer_name, c.email, c.phone
            FROM reminders r
            JOIN customers c ON r.customer_id = c.id
            WHERE r.scheduled_for <= ? AND r.completed = 0
            ORDER BY r.scheduled_for ASC
        """, (now,))
        
        rows = cursor.fetchall()
        conn.close()
        
        reminders = []
        for row in rows:
            reminders.append({
                "id": row[0],
                "customer_id": row[1],
                "type": row[2],
                "message": row[3],
                "scheduled_for": row[4],
                "completed": bool(row[5]),
                "created_at": row[6],
                "customer_name": row[7],
                "customer_email": row[8],
                "customer_phone": row[9]
            })
        
        return reminders
    
    async def complete_reminder(self, reminder_id: str) -> Optional[Dict[str, Any]]:
        """Mark a reminder as complete"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE reminders 
            SET completed = 1 
            WHERE id = ?
        """, (reminder_id,))
        
        if cursor.rowcount == 0:
            conn.close()
            return None
        
        cursor.execute("SELECT * FROM reminders WHERE id = ?", (reminder_id,))
        row = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return {
            "id": row[0],
            "customer_id": row[1],
            "type": row[2],
            "message": row[3],
            "scheduled_for": row[4],
            "completed": bool(row[5]),
            "created_at": row[6]
        }
    
    async def process_due_reminders(self) -> List[Dict[str, Any]]:
        """Process all due reminders and create follow-up actions"""
        due_reminders = await self.get_due_reminders()
        results = []
        
        for reminder in due_reminders:
            # Auto-complete the reminder
            await self.complete_reminder(reminder["id"])
            
            # Create follow-up interactions or reminders based on type
            follow_up = await self._create_follow_up_action(reminder)
            if follow_up:
                results.append({
                    "reminder": reminder,
                    "follow_up": follow_up
                })
        
        return results
    
    async def _create_follow_up_action(self, reminder: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Create appropriate follow-up action based on reminder type"""
        reminder_type = reminder["type"]
        customer_id = reminder["customer_id"]
        
        # Define follow-up intervals
        follow_up_intervals = {
            "follow_up_24h": timedelta(hours=48),  # Next: 48h follow-up
            "follow_up_48h": timedelta(days=1),    # Next: 1 day follow-up
            "follow_up_2h": timedelta(days=1),     # Next: 1 day follow-up
            "follow_up_1d": timedelta(days=7),     # Next: 7 day follow-up
            "follow_up_7d": timedelta(days=14),    # Next: 14 day follow-up
        }
        
        if reminder_type in follow_up_intervals:
            next_scheduled = datetime.now() + follow_up_intervals[reminder_type]
            
            # Create next reminder
            next_reminder = await self.create_reminder(
                customer_id=customer_id,
                reminder_type=f"follow_up_{follow_up_intervals[reminder_type].days}d" if follow_up_intervals[reminder_type].days > 0 else "follow_up_2h",
                message=f"Follow up on previous {reminder_type.replace('_', ' ')} reminder",
                scheduled_for=next_scheduled
            )
            
            # Also create an interaction record
            await self._create_interaction_record(customer_id, f"System reminder: {reminder['message']}")
            
            return next_reminder
        
        return None
    
    async def _create_interaction_record(self, customer_id: str, content: str):
        """Create an interaction record for system reminders"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        interaction_id = str(uuid.uuid4())
        
        cursor.execute("""
            INSERT INTO interactions (id, customer_id, type, content, created_at, completed)
            VALUES (?, ?, ?, ?, ?, 1)
        """, (interaction_id, customer_id, 'reminder', content, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
        
        return interaction_id
    
    async def create_automated_reminders(self, customer_id: str, pipeline_status: str):
        """Create automated reminders based on pipeline status"""
        reminder_schedules = {
            "Lead": [
                {"hours": 24, "type": "follow_up_24h", "message": "Follow up with new lead within 24 hours"},
                {"hours": 48, "type": "follow_up_48h", "message": "Second follow-up if no response"}
            ],
            "Relationship": [
                {"hours": 2, "type": "follow_up_2h", "message": "Quick check-in to build relationship"},
                {"days": 1, "type": "follow_up_1d", "message": "Continue relationship building"}
            ],
            "Invited": [
                {"days": 1, "type": "follow_up_1d", "message": "Confirm invitation response"},
                {"days": 7, "type": "follow_up_7d", "message": "Follow up on invitation if no response"}
            ],
            "Qualified": [
                {"hours": 2, "type": "follow_up_2h", "message": "Send presentation materials to qualified prospect"},
                {"hours": 24, "type": "follow_up_24h", "message": "Follow up on presentation materials"}
            ],
            "Presentation Sent": [
                {"days": 1, "type": "follow_up_1d", "message": "Follow up on presentation feedback"},
                {"days": 7, "type": "follow_up_7d", "message": "Second follow-up on presentation"}
            ],
            "Follow-up": [
                {"days": 7, "type": "follow_up_7d", "message": "Continue follow-up process"}
            ]
        }
        
        if pipeline_status in reminder_schedules:
            for schedule in reminder_schedules[pipeline_status]:
                scheduled_time = datetime.now()
                if "hours" in schedule:
                    scheduled_time += timedelta(hours=schedule["hours"])
                elif "days" in schedule:
                    scheduled_time += timedelta(days=schedule["days"])
                
                await self.create_reminder(
                    customer_id=customer_id,
                    reminder_type=schedule["type"],
                    message=schedule["message"],
                    scheduled_for=scheduled_time
                )