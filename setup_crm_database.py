#!/usr/bin/env python3
"""
Setup comprehensive CRM database schema for Flowstate-AI
Includes: Leads, Customers, Notes, Reminders, and AI Categorization
"""

import sqlite3
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
DB_PATH = PROJECT_ROOT / "godmode-state.db"

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create leads table (Frazer Method compatible)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS leads (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            external_id TEXT UNIQUE,
            name TEXT NOT NULL,
            email TEXT,
            phone TEXT,
            handle_ig TEXT,
            country TEXT,
            language TEXT DEFAULT 'no',
            lifecycle_stage TEXT DEFAULT 'lead',
            stage TEXT DEFAULT 'Lead Generation',
            pipeline TEXT DEFAULT 'Sales',
            consent_email BOOLEAN DEFAULT 0,
            consent_sms BOOLEAN DEFAULT 0,
            consent_messaging BOOLEAN DEFAULT 0,
            terms_version TEXT,
            utm_source TEXT,
            utm_medium TEXT,
            utm_campaign TEXT,
            utm_content TEXT,
            utm_term TEXT,
            score INTEGER DEFAULT 0,
            owner_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create deals table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS deals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER,
            pipeline TEXT DEFAULT 'Sales',
            stage TEXT DEFAULT 'New',
            amount REAL,
            currency TEXT DEFAULT 'NOK',
            product TEXT,
            booking_time TIMESTAMP,
            booking_status TEXT,
            owner_id TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    
    # Create quick_notes table (for the new feature)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS quick_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            raw_content TEXT NOT NULL,
            note_type TEXT DEFAULT 'general',
            lead_id INTEGER,
            lead_name TEXT,
            extracted_time TEXT,
            extracted_date TEXT,
            reminder_datetime TIMESTAMP,
            language TEXT,
            priority TEXT DEFAULT 'normal',
            status TEXT DEFAULT 'pending',
            ai_confidence REAL,
            ai_suggestions TEXT,
            requires_disambiguation BOOLEAN DEFAULT 0,
            disambiguation_options TEXT,
            created_by TEXT DEFAULT 'admin',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            processed_at TIMESTAMP,
            committed_at TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    
    # Create reminders table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER,
            lead_id INTEGER,
            reminder_datetime TIMESTAMP NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'pending',
            notification_sent BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES quick_notes(id),
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    
    # Create note_interactions table (for tracking AI interactions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS note_interactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            note_id INTEGER NOT NULL,
            interaction_type TEXT NOT NULL,
            user_response TEXT,
            ai_question TEXT,
            resolved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (note_id) REFERENCES quick_notes(id)
        )
    """)
    
    # Create lead_activities table (for tracking all interactions)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS lead_activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            lead_id INTEGER NOT NULL,
            activity_type TEXT NOT NULL,
            description TEXT,
            metadata TEXT,
            created_by TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (lead_id) REFERENCES leads(id)
        )
    """)
    
    # Insert sample data for testing
    cursor.execute("""
        INSERT OR IGNORE INTO leads (external_id, name, email, phone, stage, pipeline)
        VALUES 
            ('lead-001', 'Nora Fredriksen', 'nora.f@example.com', '+4791234567', 'Qualified', 'Sales'),
            ('lead-002', 'Nora Henriksen', 'nora.h@example.com', '+4791234568', 'New', 'Sales'),
            ('lead-003', 'Henrik Olsen', 'henrik.o@example.com', '+4791234569', 'Booked', 'Recruiting'),
            ('lead-004', 'Emma Larsen', 'emma.l@example.com', '+4791234570', 'Qualified', 'Sales'),
            ('lead-005', 'Jonas Berg', 'jonas.b@example.com', '+4791234571', 'New', 'Recruiting')
    """)
    
    conn.commit()
    conn.close()
    print("✅ Database schema created successfully!")
    print(f"📊 Database location: {DB_PATH}")

if __name__ == "__main__":
    setup_database()
