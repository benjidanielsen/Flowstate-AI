import sys
import os
import json
import sqlite3
from datetime import datetime
import sys
from maccs_client import MACCSClientV3

def initialize_maccs_v3(manus_id, repo_path):
    print(f"[{manus_id}] Initializing MACCS v3.0...")
    client = MACCSClientV3(manus_id, repo_path)
    
    # Set initial capabilities for this Manus instance
    # This should ideally be customized per Manus role
    default_capabilities = {
        "skills": ["python", "documentation", "git_workflow"],
        "specialization": "general_purpose",
        "max_concurrent_tasks": 1,
        "preferred_task_types": ["coordination", "reporting"]
    }
    if manus_id == "manus_5":
        default_capabilities = {
            "skills": ["python", "testing", "documentation", "bug_fixing", "system_architecture", "database_design", "git_workflow"],
            "specialization": "quality_assurance_and_system_architecture",
            "max_concurrent_tasks": 2,
            "preferred_task_types": ["bug_fix", "testing", "code_review", "design", "system_implementation"]
        }
    elif manus_id == "manus_2": # Example for Manus #2
        default_capabilities = {
            "skills": ["python", "ai_systems", "quality_assurance", "project_management", "system_architecture"],
            "specialization": "quality_enhancer_and_ai_systems_lead",
            "max_concurrent_tasks": 3,
            "preferred_task_types": ["approval", "design", "ai_development", "monitoring"]
        }
    # Add more Manus-specific capabilities here

    client.update_capabilities(**default_capabilities)
    client.send_heartbeat(status="INITIALIZED_MACCS_V3")
    client.close()
    print(f"[{manus_id}] MACCS v3.0 database initialized and capabilities set.")

def migrate_from_v0(manus_id, repo_path, client_v3):
    print(f"[{manus_id}] Attempting to migrate data from coordination-status.json...")
    old_coord_file = os.path.join(repo_path, ".manus-coordination/coordination-status.json")
    if not os.path.exists(old_coord_file):
        print(f"[{manus_id}] Old coordination file not found. Skipping migration.")
        return

    try:
        with open(old_coord_file, 'r') as f:
            old_data = json.load(f)

        # Migrate Manus instances and their last known status/messages
        for m_id, m_data in old_data.get("manus_instances", {}).items():
            # Update heartbeats table
            status = m_data.get("status", "UNKNOWN")
            current_task = m_data.get("current_task", "")
            last_update_str = m_data.get("last_update") or m_data.get("last_heartbeat")
            last_update = datetime.fromisoformat(last_update_str.replace('Z', '+00:00')) if last_update_str else datetime.utcnow()
            
            # Attempt to infer capabilities from old data if not explicitly set
            inferred_skills = []
            if m_data.get("role"): inferred_skills.append(m_data["role"].replace('_', ' '))
            if m_data.get("completed_work"): inferred_skills.extend([w.split(' ')[0].lower() for w in m_data["completed_work"] if w])
            inferred_skills = list(set(inferred_skills))

            client_v3.conn.execute("""
                INSERT OR REPLACE INTO heartbeats (manus_id, status, current_task, timestamp, capabilities, heartbeat_interval)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (m_id, status, current_task, last_update, json.dumps({"skills": inferred_skills, "specialization": m_data.get("role")}), 15))
            client_v3.conn.commit()

            # Migrate messages to Manus #2
            if m_data.get("message_to_manus_2") and m_id != "manus_2":
                client_v3.send_message("manus_2", "OLD_COORD_MESSAGE", 
                                       {"original_sender": m_id, "text": m_data["message_to_manus_2"]},
                                       priority="NORMAL", requires_approval=False)
            
            # Migrate messages to current manus
            if m_data.get(f"message_to_{manus_id}"):
                 client_v3.send_message(manus_id, "OLD_COORD_MESSAGE", 
                                       {"original_sender": m_id, "text": m_data[f"message_to_{manus_id}"]},
                                       priority="NORMAL", requires_approval=False)

        print(f"[{manus_id}] Migration from coordination-status.json completed successfully.")
    except Exception as e:
        print(f"[{manus_id}] Error during migration: {e}")


if __name__ == "__main__":
    # This script is meant to be run by each Manus instance to set up their local DB
    # Example usage:
    # python deploy_maccs_v3.py manus_5 /home/ubuntu/Flowstate-AI

    if len(sys.argv) < 3:
        print("Usage: python deploy_maccs_v3.py <manus_id> <repo_path>")
        sys.exit(1)

    manus_id = sys.argv[1]
    repo_path = sys.argv[2]

    # Initialize the DB and set capabilities
    initialize_maccs_v3(manus_id, repo_path)

    # Create a client instance for migration
    client_for_migration = MACCSClientV3(manus_id, repo_path)
    migrate_from_v0(manus_id, repo_path, client_for_migration)
    client_for_migration.close()

    print(f"[{manus_id}] MACCS v3.0 deployment script finished.")

