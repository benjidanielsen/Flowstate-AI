
#!/usr/bin/env python3
"""
🚀 FLOWSTATE-AI UNIFIED SUPER DASHBOARD
⚡ All-in-one interface: AI Agents + CRM + Tasks + Chat + Analytics
🎯 Mission: Single dashboard for complete system control
"""

from flask import Flask, render_template, render_template_string, jsonify, request, redirect, url_for, session
from flask_wtf.csrf import CSRFProtect, generate_csrf
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import json
from pathlib import Path
from datetime import datetime
from openai import OpenAI
import os
import subprocess
import time
import sys

# Add backend directory to path for CRM imports
sys.path.insert(0, str(Path(__file__).parent / "backend"))

PROJECT_ROOT = Path(__file__).parent
app = Flask(__name__, static_folder=PROJECT_ROOT / "static", template_folder=PROJECT_ROOT / "templates")
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24)) # Load from env or generate for dev
DB_PATH = PROJECT_ROOT / "godmode-state.db"

# Initialize OpenAI client
client = OpenAI()

# Initialize CSRFProtect
csrf = CSRFProtect(app)

# Import and register CRM blueprint
try:
    from crm_dashboard_routes import crm_bp
    app.register_blueprint(crm_bp)
    print("✅ CRM Dashboard routes registered successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not register CRM routes: {e}")

# Import and register enhanced dashboard API
try:
    from api_dashboard_enhanced import dashboard_api
    app.register_blueprint(dashboard_api)
    print("✅ Enhanced Dashboard API registered successfully")
except Exception as e:
    print(f"⚠️  Warning: Could not register enhanced dashboard API: {e}")

# --- Helper Functions ---
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# --- Authentication --- 
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "benjidanielsen")
ADMIN_PASSWORD_HASH = os.environ.get("ADMIN_PASSWORD_HASH", generate_password_hash("Sagemaster123", method=\'pbkdf2:sha256\'))

# In-memory store for login attempts (for rate limiting)
login_attempts = {}
LOGIN_ATTEMPT_LIMIT = 5
LOGIN_ATTEMPT_WINDOW_SECONDS = 300 # 5 minutes

@app.route("/login", methods=["GET", "POST"])
def login():
    # Generate CSRF token for the form
    csrf_token = generate_csrf()
    if request.method == "POST":
        # Rate limiting check
        client_ip = request.remote_addr
        current_time = time.time()

        if client_ip in login_attempts:
            attempts, first_attempt_time = login_attempts[client_ip]
            if current_time - first_attempt_time > LOGIN_ATTEMPT_WINDOW_SECONDS:
                # Reset attempts after window expires
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
            return render_template_string("""
                <p>Invalid credentials. <a href="/login">Try again</a></p>
            """, error="Invalid credentials", csrf_token=csrf_token)
    return render_template_string("""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Admin Login</title>
            <style>
                body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; display: flex; justify-content: center; align-items: center; min-height: 100vh; margin: 0; }
                .login-container { background: rgba(255,255,255,0.1); padding: 40px; border-radius: 15px; box-shadow: 0 5px 20px rgba(0,0,0,0.2); text-align: center; }
                .login-container h2 { margin-bottom: 30px; font-size: 2em; }
                .login-container input { width: 100%; padding: 12px 15px; margin-bottom: 20px; border: none; border-radius: 8px; background: rgba(255,255,255,0.9); color: #333; font-size: 1em; }
                .login-container button { width: 100%; padding: 12px 15px; border: none; border-radius: 8px; background: #28a745; color: white; font-size: 1.1em; cursor: pointer; transition: background 0.3s; }
                .login-container button:hover { background: #218838; }
            </style>
        </head>
        <body>
            <div class="login-container">
                <h2>Flowstate-AI Admin Login</h2>
                <form method="post">
                    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
                    <input type="text" name="username" placeholder="Username" required>
                    <input type="password" name="password" placeholder="Password" required>
                    <button type="submit">Login</button>
                </form>
            </div>
        </body>
        </html>
    """, csrf_token=csrf_token)

@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect(url_for("login"))

# --- Dashboard Routes ---
@app.route("/")
def index():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard_v2.html")

@app.route("/v1")
def dashboard_v1():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("dashboard_enhanced.html")

@app.route("/classic")
def classic_dashboard():
    if not session.get("logged_in"):
        return redirect(url_for("login"))
    return render_template("index.html")

# --- API Endpoints ---
@app.route("/api/stats")
def get_stats():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM agents WHERE status = 'active'")
    active_agents = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('pending', 'in_progress')")
    pending_tasks = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM leads")
    total_leads = cursor.fetchone()[0]

    # Assuming 'completed_at' is a timestamp and we want tasks completed today
    today = datetime.now().strftime("%Y-%m-%d")
    cursor.execute("SELECT COUNT(*) FROM tasks WHERE status = 'completed' AND completed_at LIKE ? || '%'"), (today,))
    completed_today = cursor.fetchone()[0]

    conn.close()
    return jsonify({
        "agents": active_agents,
        "tasks": pending_tasks,
        "leads": total_leads,
        "completed_today": completed_today
    })

@app.route("/api/agents")
def get_agents():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT
            a.agent_number,
            a.human_name,
            a.role,
            a.specialization,
            a.personality_traits,
            a.profile_photo_url,
            a.gender,
            as_t.status,
            as_t.current_task,
            as_t.last_heartbeat,
            a.tasks_completed,
            a.tasks_failed
        FROM agents a
        LEFT JOIN agent_status as_t ON a.agent_number = as_t.agent_number
        ORDER BY a.agent_number ASC
    """)
    
    agents = []
    for row in cursor.fetchall():
        # Process profile photo URL to use local storage if available
        profile_photo = row["profile_photo_url"]
        human_name_lower = row["human_name"].lower() if row["human_name"] else ""
        
        # Check if local profile photo exists
        local_photo_path = PROJECT_ROOT / "static" / "agent_profiles" / f"{human_name_lower}.jpeg"
        if local_photo_path.exists():
            profile_photo = f"/static/agent_profiles/{human_name_lower}.jpeg"
        elif not profile_photo or profile_photo == "":
            # Generate default avatar URL based on initials and gender
            profile_photo = generate_avatar_url(row["human_name"], row["gender"])
            
        agents.append({
            "agent_number": row["agent_number"],
            "human_name": row["human_name"],
            "role": row["role"],
            "specialization": row["specialization"],
            "personality_traits": row["personality_traits"],
            "profile_photo_url": profile_photo,
            "gender": row["gender"],
            "status": row["status"] if row["status"] else "offline",
            "current_task": row["current_task"] if row["current_task"] else "Idle",
            "last_heartbeat": row["last_heartbeat"],
            "tasks_completed": row["tasks_completed"],
            "tasks_failed": row["tasks_failed"]
        })
    
    conn.close()
    return jsonify(agents)

def generate_avatar_url(name, gender):
    """Generate a default avatar URL using UI Avatars service"""
    if not name:
        name = "AI Agent"
    
    # Get initials
    name_parts = name.split()
    initials = "".join([part[0].upper() for part in name_parts[:2]])
    
    # Choose background color based on gender
    if gender and gender.lower() == "male":
        bg_color = "4F46E5"  # Primary color
    else:
        bg_color = "06B6D4"  # Secondary color
    
    # Generate avatar URL
    return f"https://ui-avatars.com/api/?name={initials}&background={bg_color}&color=fff&size=200&bold=true"

@app.route("/api/tasks")
def get_tasks():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id, title, status, priority, assigned_to, completed_at FROM tasks ORDER BY priority DESC, id ASC")
    tasks = cursor.fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route("/api/crm")
def get_crm_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Pipeline stages (Frazer Method)
    stages = ["Lead Generation", "Qualification", "Nurturing", "Conversion", "Retention"]
    pipeline_data = []
    for stage in stages:
        cursor.execute("SELECT name, email, stage FROM leads WHERE stage = ?", (stage,))
        leads_in_stage = cursor.fetchall()
        pipeline_data.append({"name": stage, "leads": [dict(lead) for lead in leads_in_stage]})

    # Recent leads (for home tab or separate display)
    cursor.execute("SELECT name, email, stage FROM leads ORDER BY id DESC LIMIT 5")
    recent_leads = cursor.fetchall()

    conn.close()
    return jsonify({"pipeline": pipeline_data, "recent_leads": [dict(lead) for lead in recent_leads]})

@app.route("/api/activity_log")
def get_activity_log():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT agent_name, agent_number, description, details, timestamp FROM activity_log ORDER BY timestamp DESC LIMIT 20")
    activities = cursor.fetchall()
    conn.close()
    return jsonify([dict(activity) for activity in activities])

@app.route("/api/system_status")
def get_system_status():
    # Placeholder for actual system status data
    uptime = subprocess.check_output(["uptime", "-p"]).decode("utf-8").strip()
    python_version = subprocess.check_output(["python3.11", "--version"]).decode("utf-8").strip()
    nodejs_version = subprocess.check_output(["node", "--version"]).decode("utf-8").strip()
    
    db_size = os.path.getsize(DB_PATH) / (1024 * 1024) # Size in MB
    
    try:
        last_git_commit = subprocess.check_output(["git", "log", "-1", "--pretty=%h %s"]).decode("utf-8").strip()
    except subprocess.CalledProcessError:
        last_git_commit = "N/A"

    return jsonify({
        "uptime": uptime,
        "python_version": python_version,
        "nodejs_version": nodejs_version,
        "db_size": f"{db_size:.2f} MB",
        "last_git_commit": last_git_commit
    })

@app.route("/api/chat", methods=["POST"])
def chat_with_pm():
    user_message = request.json.get("message")
    if not user_message:
        return jsonify({"response": "Please provide a message."}), 400

    # Simulate AI response from Project Manager
    # In a real scenario, this would involve calling the Project Manager AI agent
    # via its internal API or message queue.
    ai_response = f"PM AI: Received your message: '{user_message}'. I'm processing this now."
    
    # Log the interaction (optional, for audit/learning)
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO activity_log (agent_name, agent_number, description, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                   ("User", "N/A", "Chat with PM AI", user_message, datetime.now().isoformat()))
    cursor.execute("INSERT INTO activity_log (agent_name, agent_number, description, details, timestamp) VALUES (?, ?, ?, ?, ?)",
                   ("Project Manager AI", "N/A", "Responded to chat", ai_response, datetime.now().isoformat()))
    conn.commit()
    conn.close()

    return jsonify({"response": ai_response})

@app.route("/api/quick_note", methods=["POST"])
def create_quick_note():
    """Process and save a quick note with AI categorization"""
    from brain.notes_processor import NotesProcessor
    
    note_text = request.json.get("note")
    if not note_text:
        return jsonify({"error": "Note text is required"}), 400
    
    conn = get_db_connection()
    processor = NotesProcessor()
    
    try:
        # Process the note
        result = processor.process_note(note_text, conn)
        
        # Save to database
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quick_notes (
                content, raw_content, note_type, language, 
                extracted_time, extracted_date, reminder_datetime,
                priority, ai_confidence, ai_suggestions,
                requires_disambiguation, disambiguation_options, status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            result['ai_analysis'].get('summary', note_text[:200]),
            note_text,
            result['note_type'],
            result['language'],
            result['time_info'].get('time'),
            result['time_info'].get('date'),
            result['time_info'].get('datetime'),
            result['priority'],
            result['confidence'],
            json.dumps(result['ai_analysis']),
            result['requires_disambiguation'],
            json.dumps(result['lead_matches']),
            'pending' if result['requires_disambiguation'] else 'processed'
        ))
        
        note_id = cursor.lastrowid
        
        # If there's a clear match (only one lead), auto-assign
        if len(result['lead_matches']) == 1:
            lead = result['lead_matches'][0]
            cursor.execute("""
                UPDATE quick_notes 
                SET lead_id = ?, lead_name = ?, status = 'auto_assigned'
                WHERE id = ?
            """, (lead['id'], lead['name'], note_id))
            
            # Create reminder if time was extracted
            if result['time_info'].get('datetime'):
                cursor.execute("""
                    INSERT INTO reminders (note_id, lead_id, reminder_datetime, title, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    note_id,
                    lead['id'],
                    result['time_info']['datetime'],
                    f"Follow up: {lead['name']}",
                    note_text
                ))
        
        conn.commit()
        
        response_data = {
            "note_id": note_id,
            "status": "success",
            "requires_disambiguation": result['requires_disambiguation'],
            "lead_matches": result['lead_matches'],
            "time_info": result['time_info'],
            "ai_analysis": result['ai_analysis'],
            "language": result['language']
        }
        
        conn.close()
        return jsonify(response_data)
        
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route("/api/quick_note/<int:note_id>/resolve", methods=["POST"])
def resolve_note_disambiguation(note_id):
    """Resolve disambiguation by selecting a specific lead"""
    lead_id = request.json.get("lead_id")
    action = request.json.get("action")  # "assign" or "skip"
    
    if not lead_id and action != "skip":
        return jsonify({"error": "lead_id required"}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        if action == "skip":
            cursor.execute("""
                UPDATE quick_notes 
                SET status = 'skipped', processed_at = ?
                WHERE id = ?
            """, (datetime.now().isoformat(), note_id))
        else:
            # Get lead info
            cursor.execute("SELECT name FROM leads WHERE id = ?", (lead_id,))
            lead = cursor.fetchone()
            
            if not lead:
                return jsonify({"error": "Lead not found"}), 404
            
            # Update note
            cursor.execute("""
                UPDATE quick_notes 
                SET lead_id = ?, lead_name = ?, status = 'assigned', 
                    processed_at = ?, committed_at = ?
                WHERE id = ?
            """, (lead_id, lead['name'], datetime.now().isoformat(), 
                  datetime.now().isoformat(), note_id))
            
            # Get note info for reminder
            cursor.execute("SELECT content, reminder_datetime FROM quick_notes WHERE id = ?", (note_id,))
            note = cursor.fetchone()

            # Create reminder if time was extracted
            if note and note['reminder_datetime']:
                cursor.execute("""
                    INSERT INTO reminders (note_id, lead_id, reminder_datetime, title, description)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    note_id,
                    lead_id,
                    note['reminder_datetime'],
                    f"Follow up: {lead['name']}",
                    note['content']
                ))
        
        conn.commit()
        conn.close()
        return jsonify({"status": "success"})
        
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Ensure the database exists and has the necessary tables
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            agent_number INTEGER PRIMARY KEY AUTOINCREMENT,
            human_name TEXT NOT NULL,
            role TEXT NOT NULL,
            specialization TEXT,
            personality_traits TEXT,
            profile_photo_url TEXT,
            gender TEXT,
            tasks_completed INTEGER DEFAULT 0,
            tasks_failed INTEGER DEFAULT 0
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS agent_status (
            agent_number INTEGER PRIMARY KEY,
            status TEXT NOT NULL,
            current_task TEXT,
            last_heartbeat TEXT,
            FOREIGN KEY (agent_number) REFERENCES agents (agent_number)
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            status TEXT NOT NULL,
            priority TEXT,
            assigned_to TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            completed_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            stage TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS activity_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_name TEXT,
            agent_number TEXT,
            description TEXT NOT NULL,
            details TEXT,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quick_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            raw_content TEXT NOT NULL,
            note_type TEXT,
            language TEXT,
            extracted_time TEXT,
            extracted_date TEXT,
            reminder_datetime TEXT,
            priority TEXT,
            ai_confidence REAL,
            ai_suggestions TEXT,
            requires_disambiguation BOOLEAN,
            disambiguation_options TEXT,
            status TEXT,
            lead_id INTEGER,
            lead_name TEXT,
            processed_at TEXT,
            committed_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER,
            lead_id INTEGER,
            reminder_datetime TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES quick_notes (id),
            FOREIGN KEY (lead_id) REFERENCES leads (id)
        )
    """)
    conn.commit()
    conn.close()
    app.run(debug=os.environ.get("FLASK_DEBUG") == "1", port=5000, host="0.0.0.0")

