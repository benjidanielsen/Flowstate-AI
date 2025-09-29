import sqlite3
from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any, Optional
import os
import json

class NBAService:
    def __init__(self):
        self.db_path = os.getenv('DATABASE_URL', '../data/flowstate.db')
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    async def get_recommendations(self, customer_id: Optional[str] = None, limit: int = 10) -> List[Dict[str, Any]]:
        """Get Next Best Action recommendations"""
        if customer_id:
            return await self._get_customer_recommendations(customer_id)
        else:
            return await self._get_global_recommendations(limit)
    
    async def _get_customer_recommendations(self, customer_id: str) -> List[Dict[str, Any]]:
        """Get NBA recommendations for a specific customer"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get customer details
        cursor.execute("""
            SELECT id, name, email, phone, status, created_at, updated_at, notes, next_action, next_action_date
            FROM customers WHERE id = ?
        """, (customer_id,))
        
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            return []
        
        # Get recent interactions
        cursor.execute("""
            SELECT type, content, created_at, completed
            FROM interactions 
            WHERE customer_id = ? 
            ORDER BY created_at DESC LIMIT 5
        """, (customer_id,))
        
        interactions = cursor.fetchall()
        
        # Get pending reminders
        cursor.execute("""
            SELECT type, message, scheduled_for
            FROM reminders 
            WHERE customer_id = ? AND completed = 0
            ORDER BY scheduled_for ASC
        """, (customer_id,))
        
        reminders = cursor.fetchall()
        conn.close()
        
        # Analyze and generate recommendations
        recommendations = []
        customer_data = {
            "id": customer[0],
            "name": customer[1],
            "email": customer[2],
            "phone": customer[3],
            "status": customer[4],
            "created_at": customer[5],
            "updated_at": customer[6],
            "notes": customer[7],
            "next_action": customer[8],
            "next_action_date": customer[9]
        }
        
        # Analyze based on pipeline status
        recommendations.extend(self._analyze_pipeline_status(customer_data))
        
        # Analyze based on interaction history
        recommendations.extend(self._analyze_interaction_history(customer_data, interactions))
        
        # Analyze based on time since last contact
        recommendations.extend(self._analyze_contact_timing(customer_data, interactions))
        
        # Check for overdue next actions
        recommendations.extend(self._check_overdue_actions(customer_data))
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[:5]
    
    async def _get_global_recommendations(self, limit: int) -> List[Dict[str, Any]]:
        """Get global NBA recommendations across all customers"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        recommendations = []
        
        # Get customers with overdue next actions
        cursor.execute("""
            SELECT id, name, status, next_action, next_action_date
            FROM customers 
            WHERE next_action_date IS NOT NULL AND next_action_date < ?
            ORDER BY next_action_date ASC
        """, (datetime.now(timezone.utc).isoformat(),))
        
        overdue_customers = cursor.fetchall()
        
        for customer in overdue_customers:
            recommendations.append({
                "customer_id": customer[0],
                "customer_name": customer[1],
                "action_type": "overdue_next_action",
                "title": f"Overdue: {customer[3]}",
                "description": f"Next action for {customer[1]} was due on {customer[4]}",
                "priority": 90,
                "urgency": "high",
                "pipeline_status": customer[2]
            })
        
        # Get customers without recent interactions
        seven_days_ago = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
        cursor.execute("""
            SELECT c.id, c.name, c.status, c.updated_at,
                   MAX(i.created_at) as last_interaction
            FROM customers c
            LEFT JOIN interactions i ON c.id = i.customer_id
            WHERE c.status NOT IN ('SIGNED-UP') 
            GROUP BY c.id
            HAVING last_interaction IS NULL OR last_interaction < ?
            ORDER BY c.updated_at ASC
        """, (seven_days_ago,))
        
        inactive_customers = cursor.fetchall()
        
        for customer in inactive_customers:
            days_since_update = (datetime.now(timezone.utc) - datetime.fromisoformat(customer[3].replace('Z', '+00:00'))).days
            priority = 70 if days_since_update > 14 else 50
            
            recommendations.append({
                "customer_id": customer[0],
                "customer_name": customer[1],
                "action_type": "follow_up_needed",
                "title": f"Follow up with {customer[1]}",
                "description": f"No interaction in {days_since_update} days",
                "priority": priority,
                "urgency": "medium" if days_since_update > 14 else "low",
                "pipeline_status": customer[2]
            })
        
        # Get customers ready for next pipeline stage
        cursor.execute("""
            SELECT id, name, status, updated_at
            FROM customers 
            WHERE status IN ('Relationship', 'Invited', 'Qualified', 'Presentation Sent')
            AND updated_at < ?
            ORDER BY updated_at ASC
        """, ((datetime.now(timezone.utc) - timedelta(days=3)).isoformat(),))
        
        progression_candidates = cursor.fetchall()
        
        for customer in progression_candidates:
            recommendations.append({
                "customer_id": customer[0],
                "customer_name": customer[1],
                "action_type": "pipeline_progression",
                "title": f"Consider moving {customer[1]} to next stage",
                "description": f"Customer has been in {customer[2]} stage for several days",
                "priority": 60,
                "urgency": "medium",
                "pipeline_status": customer[2]
            })
        
        conn.close()
        
        # Sort by priority and return top recommendations
        recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return recommendations[:limit]
    
    def _analyze_pipeline_status(self, customer: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate recommendations based on pipeline status"""
        recommendations = []
        status = customer["status"]
        
        pipeline_actions = {
            "Lead": {
                "title": "Initial contact and qualification",
                "description": "Reach out to establish relationship and qualify interest",
                "priority": 80
            },
            "Relationship": {
                "title": "Build rapport and present opportunity",
                "description": "Continue building relationship and present the opportunity",
                "priority": 75
            },
            "Invited": {
                "title": "Confirm invitation and follow up",
                "description": "Ensure they attend the presentation or event",
                "priority": 85
            },
            "Qualified": {
                "title": "Send presentation materials",
                "description": "Provide detailed presentation and materials",
                "priority": 90
            },
            "Presentation Sent": {
                "title": "Follow up on presentation",
                "description": "Get feedback and address questions",
                "priority": 95
            },
            "Follow-up": {
                "title": "Continue follow-up process",
                "description": "Maintain contact and work toward closing",
                "priority": 70
            }
        }
        
        if status in pipeline_actions:
            action = pipeline_actions[status]
            recommendations.append({
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "action_type": "pipeline_action",
                "title": action["title"],
                "description": action["description"],
                "priority": action["priority"],
                "urgency": "high" if action["priority"] > 80 else "medium",
                "pipeline_status": status
            })
        
        return recommendations
    
    def _analyze_interaction_history(self, customer: Dict[str, Any], interactions: List[tuple]) -> List[Dict[str, Any]]:
        """Analyze interaction patterns and suggest actions"""
        recommendations = []
        
        if not interactions:
            recommendations.append({
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "action_type": "first_contact",
                "title": "Make first contact",
                "description": f"No interactions recorded for {customer['name']} yet",
                "priority": 85,
                "urgency": "high",
                "pipeline_status": customer["status"]
            })
            return recommendations
        
        # Check for incomplete interactions
        incomplete_interactions = [i for i in interactions if not i[3]]  # i[3] is completed
        if incomplete_interactions:
            recommendations.append({
                "customer_id": customer["id"],
                "customer_name": customer["name"],
                "action_type": "complete_interaction",
                "title": "Complete pending interactions",
                "description": f"{len(incomplete_interactions)} incomplete interactions need attention",
                "priority": 75,
                "urgency": "medium",
                "pipeline_status": customer["status"]
            })
        
        return recommendations
    
    def _analyze_contact_timing(self, customer: Dict[str, Any], interactions: List[tuple]) -> List[Dict[str, Any]]:
        """Analyze timing patterns and suggest optimal contact times"""
        recommendations = []
        
        if interactions:
            last_interaction_date = interactions[0][2]  # Most recent interaction
            last_contact = datetime.fromisoformat(last_interaction_date.replace('Z', '+00:00'))
            days_since_contact = (datetime.now(timezone.utc) - last_contact).days
            
            if days_since_contact > 7:
                recommendations.append({
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "action_type": "reconnect",
                    "title": f"Reconnect with {customer['name']}",
                    "description": f"Last contact was {days_since_contact} days ago",
                    "priority": 65,
                    "urgency": "medium" if days_since_contact > 14 else "low",
                    "pipeline_status": customer["status"]
                })
        
        return recommendations
    
    def _check_overdue_actions(self, customer: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check for overdue next actions"""
        recommendations = []
        
        if customer["next_action_date"]:
            due_date = datetime.fromisoformat(customer["next_action_date"].replace('Z', '+00:00'))
            if due_date < datetime.now(timezone.utc):
                days_overdue = (datetime.now(timezone.utc) - due_date).days
                recommendations.append({
                    "customer_id": customer["id"],
                    "customer_name": customer["name"],
                    "action_type": "overdue_action",
                    "title": f"Overdue: {customer['next_action']}",
                    "description": f"Action was due {days_overdue} days ago",
                    "priority": 95,
                    "urgency": "critical",
                    "pipeline_status": customer["status"]
                })
        
        return recommendations
    
    async def analyze_and_generate_recommendations(self) -> List[Dict[str, Any]]:
        """Analyze all customer data and generate comprehensive recommendations"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Get all active customers
        cursor.execute("""
            SELECT id FROM customers WHERE status != 'SIGNED-UP'
        """)
        
        customer_ids = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        all_recommendations = []
        for customer_id in customer_ids:
            customer_recs = await self._get_customer_recommendations(customer_id)
            all_recommendations.extend(customer_recs)
        
        # Sort by priority and return
        all_recommendations.sort(key=lambda x: x["priority"], reverse=True)
        return all_recommendations