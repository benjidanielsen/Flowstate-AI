"""
Enhanced Dashboard API Endpoints
Provides data for the modern unified dashboard
"""

from flask import Blueprint, jsonify
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

dashboard_api = Blueprint('dashboard_api', __name__)

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@dashboard_api.route("/api/dashboard/stats")
def get_dashboard_stats():
    """Get overview statistics for the dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Active agents
        cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
        active_agents = cursor.fetchone()[0]
        
        # Pending tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'pending'")
        pending_tasks = cursor.fetchone()[0]
        
        # Completed today
        today = datetime.now().strftime("%Y-%m-%d")
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND completed_at LIKE ? || '%'", (today,))
        completed_today = cursor.fetchone()[0]
        
        # Running tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'running'")
        running_tasks = cursor.fetchone()[0]
        
        # Failed tasks
        cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'failed'")
        failed_tasks = cursor.fetchone()[0]
        
        # Total tasks
        cursor.execute("SELECT COUNT(*) FROM tasks")
        total_tasks = cursor.fetchone()[0]
        
        conn.close()
        
        return jsonify({
            "active_agents": active_agents,
            "pending_tasks": pending_tasks,
            "completed_today": completed_today,
            "running_tasks": running_tasks,
            "failed_tasks": failed_tasks,
            "total_tasks": total_tasks,
            "system_health": calculate_system_health(active_agents, failed_tasks, total_tasks)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_api.route("/api/tasks/recent")
def get_recent_tasks():
    """Get recent tasks for the dashboard."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                id, title, description, status, priority, created_at, updated_at, completed_at
            FROM tasks
            ORDER BY created_at DESC
            LIMIT 20
        """)
        
        tasks = []
        for row in cursor.fetchall():
            tasks.append({
                "id": row["id"],
                "title": row["title"],
                "description": row["description"],
                "status": row["status"],
                "priority": row["priority"],
                "created_at": row["created_at"],
                "updated_at": row["updated_at"],
                "completed_at": row["completed_at"]
            })
        
        conn.close()
        return jsonify(tasks)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_api.route("/api/agents/status")
def get_agents_status():
    """Get status of all AI agents."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                a.agent_number,
                a.human_name,
                a.role,
                a.status,
                a.tasks_completed,
                a.tasks_failed,
                as_t.current_task,
                as_t.last_heartbeat
            FROM agents a
            LEFT JOIN agent_status as_t ON a.agent_number = as_t.agent_number
            ORDER BY a.agent_number ASC
        """)
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "agent_number": row["agent_number"],
                "human_name": row["human_name"],
                "role": row["role"],
                "status": row["status"],
                "tasks_completed": row["tasks_completed"],
                "tasks_failed": row["tasks_failed"],
                "current_task": row["current_task"],
                "last_heartbeat": row["last_heartbeat"]
            })
        
        conn.close()
        return jsonify(agents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_api.route("/api/analytics/activity")
def get_activity_analytics():
    """Get activity analytics for charts."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get tasks completed per day for the last 7 days
        activity_data = []
        for i in range(6, -1, -1):
            date = (datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND completed_at LIKE ? || '%'",
                (date,)
            )
            count = cursor.fetchone()[0]
            activity_data.append({
                "date": date,
                "completed": count
            })
        
        conn.close()
        return jsonify(activity_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@dashboard_api.route("/api/analytics/agents")
def get_agent_analytics():
    """Get agent performance analytics."""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                human_name,
                tasks_completed,
                tasks_failed,
                status
            FROM agents
            ORDER BY tasks_completed DESC
            LIMIT 10
        """)
        
        agents = []
        for row in cursor.fetchall():
            agents.append({
                "name": row["human_name"],
                "completed": row["tasks_completed"],
                "failed": row["tasks_failed"],
                "status": row["status"],
                "success_rate": calculate_success_rate(row["tasks_completed"], row["tasks_failed"])
            })
        
        conn.close()
        return jsonify(agents)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def calculate_system_health(active_agents, failed_tasks, total_tasks):
    """Calculate overall system health percentage."""
    if total_tasks == 0:
        return 100
    
    # Base health on agent activity and task success rate
    agent_health = min(100, active_agents * 20)  # Up to 100% with 5+ active agents
    task_success_rate = ((total_tasks - failed_tasks) / total_tasks) * 100 if total_tasks > 0 else 100
    
    # Weighted average
    overall_health = (agent_health * 0.4 + task_success_rate * 0.6)
    return round(overall_health, 1)

def calculate_success_rate(completed, failed):
    """Calculate success rate percentage."""
    total = completed + failed
    if total == 0:
        return 100
    return round((completed / total) * 100, 1)
