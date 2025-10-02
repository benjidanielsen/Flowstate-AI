#!/usr/bin/env python3.11
"""
Migrate Legacy Tasks to MACCS v3.0
===================================
This script migrates tasks from the legacy Git-based coordination system
(AVAILABLE_TASKS.md) into the MACCS v3.0 SQLite database.

Author: Manus 7
Date: October 2, 2025
"""

import sys
import os
from datetime import datetime, timedelta

# Add maccs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'maccs'))

# Import the MACCS client
import maccs_client
MACCSClientV3 = maccs_client.MACCSClientV3

# Task definitions from AVAILABLE_TASKS.md
LEGACY_TASKS = [
    {
        'task_id': 'TASK-101',
        'title': 'Fix Frontend Customer Display',
        'description': 'Frontend not showing customers from API. Need to debug why customers list is empty. Steps: 1) Check API fetch in frontend, 2) Verify data mapping, 3) Fix display logic, 4) Test with existing customers',
        'required_skills': ['frontend', 'react', 'typescript', 'debugging'],
        'priority': 'HIGH',
        'estimated_effort': '15 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-102',
        'title': 'Build Qualification Questionnaire UI',
        'description': 'Create the "Prospect\'s WHY" qualification form. Steps: 1) Create QualificationQuestionnaire.tsx component, 2) Add questions from Frazer Method, 3) Integrate with qualification API, 4) Add to customer detail view',
        'required_skills': ['frontend', 'react', 'typescript', 'ui_design'],
        'priority': 'HIGH',
        'estimated_effort': '30 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-103',
        'title': 'Implement Follow-up Reminders UI',
        'description': 'Build UI for viewing and managing follow-up reminders. Steps: 1) Create RemindersPanel component, 2) Fetch reminders from API, 3) Display upcoming reminders, 4) Add mark-as-complete functionality',
        'required_skills': ['frontend', 'react', 'typescript', 'ui_design'],
        'priority': 'HIGH',
        'estimated_effort': '25 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-104',
        'title': 'Build Calendar Integration',
        'description': 'Create calendar view for interactions and reminders. Steps: 1) Install calendar library, 2) Create Calendar component, 3) Fetch events from API, 4) Add click-to-view functionality',
        'required_skills': ['frontend', 'react', 'typescript', 'calendar_integration'],
        'priority': 'MEDIUM',
        'estimated_effort': '40 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-105',
        'title': 'Add Pipeline Visualization',
        'description': 'Create visual pipeline board (Kanban style). Steps: 1) Create PipelineBoard component, 2) Add drag-and-drop functionality, 3) Integrate with move-to-next-stage API, 4) Add customer cards',
        'required_skills': ['frontend', 'react', 'typescript', 'drag_and_drop', 'ui_design'],
        'priority': 'MEDIUM',
        'estimated_effort': '30 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-106',
        'title': 'Build Interaction Timeline',
        'description': 'Create timeline view of all interactions with a customer. Steps: 1) Create InteractionTimeline component, 2) Fetch interactions from API, 3) Display chronologically, 4) Add filtering options',
        'required_skills': ['frontend', 'react', 'typescript', 'ui_design'],
        'priority': 'MEDIUM',
        'estimated_effort': '25 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=2)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-107',
        'title': 'Add Export Functionality',
        'description': 'Export customer data to CSV/Excel. Steps: 1) Create export service, 2) Add export button to UI, 3) Generate CSV from customer data, 4) Trigger download',
        'required_skills': ['frontend', 'backend', 'data_export'],
        'priority': 'LOW',
        'estimated_effort': '20 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-108',
        'title': 'Build Settings Page',
        'description': 'Create settings page for user preferences. Steps: 1) Create Settings component, 2) Add notification preferences, 3) Add pipeline stage customization, 4) Save to backend',
        'required_skills': ['frontend', 'backend', 'ui_design'],
        'priority': 'LOW',
        'estimated_effort': '30 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-109',
        'title': 'Add Search Functionality',
        'description': 'Improve search across customers. Steps: 1) Add advanced search filters, 2) Search by multiple fields, 3) Add search history, 4) Optimize search performance',
        'required_skills': ['frontend', 'backend', 'search_optimization'],
        'priority': 'LOW',
        'estimated_effort': '20 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=3)).isoformat() + 'Z',
    },
    {
        'task_id': 'TASK-110',
        'title': 'End-to-End Testing',
        'description': 'Complete E2E test suite. Steps: 1) Test customer creation flow, 2) Test pipeline progression, 3) Test qualification process, 4) Test follow-up automation',
        'required_skills': ['testing', 'e2e_testing', 'automation'],
        'priority': 'HIGH',
        'estimated_effort': '45 minutes',
        'deadline': (datetime.utcnow() + timedelta(days=1)).isoformat() + 'Z',
    },
]

def main():
    """Main migration function."""
    print("[migrate_legacy_tasks] Starting migration of legacy tasks to MACCS v3.0...")
    
    # Initialize MACCS client
    repo_path = os.path.dirname(os.path.abspath(__file__))
    client = MACCSClientV3('manus_migration', repo_path)
    
    try:
        # Migrate each task
        for task in LEGACY_TASKS:
            print(f"[migrate_legacy_tasks] Migrating {task['task_id']}: {task['title']}")
            
            # Post task to MACCS v3.0
            task_id = client.post_task(
                title=task['title'],
                description=task['description'],
                required_skills=task['required_skills'],
                priority=task['priority'],
                estimated_effort=task['estimated_effort'],
                deadline=task['deadline']
            )
            
            # Update the task_id to match the legacy task ID
            client.conn.execute("""
                UPDATE tasks SET task_id = ? WHERE task_id = ?
            """, (task['task_id'], task_id))
            client.conn.commit()
            
            print(f"[migrate_legacy_tasks] ✓ Successfully migrated {task['task_id']}")
        
        print(f"[migrate_legacy_tasks] Migration complete! {len(LEGACY_TASKS)} tasks added to MACCS v3.0")
        
    except Exception as e:
        print(f"[migrate_legacy_tasks] Error during migration: {e}")
        raise
    finally:
        client.close()

if __name__ == '__main__':
    main()
