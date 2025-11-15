#!/usr/bin/env python3
"""Airtable → SQLite sync utility for the Flowstate-AI sandbox."""
from __future__ import annotations

import argparse
import datetime as dt
import logging
import os
import sqlite3
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import requests

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DB_PATH = PROJECT_ROOT / "godmode-state.db"

FRAZER_STAGE_ORDER = [
    "Lead",
    "Relationship",
    "Invited",
    "Qualified",
    "Presentation Sent",
    "Follow-Up",
    "Team Member",
]

STAGE_PRIORITY = {
    "Lead": "low",
    "Relationship": "medium",
    "Invited": "medium",
    "Qualified": "high",
    "Presentation Sent": "high",
    "Follow-Up": "urgent",
    "Team Member": "low",
}


class AirtableBridge:
    """Synchronize Airtable tables into the SQLite structures used by the Flask dashboard."""

    def __init__(self, api_key: str, base_id: str, db_path: Path, dry_run: bool = False):
        self.api_key = api_key
        self.base_id = base_id
        self.db_path = db_path
        self.dry_run = dry_run
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {self.api_key}"})
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        self.ensure_schema()

    def ensure_schema(self) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                stage TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                owner TEXT,
                source TEXT,
                last_touch TEXT
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                status TEXT NOT NULL,
                priority TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                completed_at TEXT,
                assigned_to TEXT,
                due_date TEXT
            )
            """
        )
        self._ensure_column("tasks", "assigned_to", "TEXT")
        self._ensure_column("tasks", "due_date", "TEXT")
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS activity_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                agent_number TEXT,
                description TEXT NOT NULL,
                details TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
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
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER,
                lead_id INTEGER,
                reminder_datetime TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS airtable_sync_state (
                airtable_id TEXT PRIMARY KEY,
                local_table TEXT NOT NULL,
                local_id INTEGER NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        self.conn.commit()

    def _ensure_column(self, table: str, column: str, definition: str) -> None:
        cursor = self.conn.execute(f"PRAGMA table_info({table})")
        columns = {row[1] for row in cursor.fetchall()}
        if column not in columns:
            logging.info("Adding missing column %s.%s", table, column)
            self.conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")
            self.conn.commit()

    # --- Airtable helpers -------------------------------------------------
    def fetch_records(self, table: str, view: Optional[str] = None) -> List[dict]:
        records: List[dict] = []
        offset: Optional[str] = None
        while True:
            params = {}
            if view:
                params["view"] = view
            if offset:
                params["offset"] = offset
            url = f"https://api.airtable.com/v0/{self.base_id}/{table}"
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()
            payload = response.json()
            records.extend(payload.get("records", []))
            offset = payload.get("offset")
            if not offset:
                break
        return records

    # --- SQLite helpers ---------------------------------------------------
    def _lookup_sync(self, airtable_id: str, local_table: str) -> Optional[int]:
        cursor = self.conn.execute(
            "SELECT local_id FROM airtable_sync_state WHERE airtable_id = ? AND local_table = ?",
            (airtable_id, local_table),
        )
        row = cursor.fetchone()
        return int(row[0]) if row else None

    def _upsert_sync(self, airtable_id: str, local_table: str, local_id: int) -> None:
        self.conn.execute(
            """
            INSERT INTO airtable_sync_state (airtable_id, local_table, local_id, updated_at)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(airtable_id) DO UPDATE SET
                local_table = excluded.local_table,
                local_id = excluded.local_id,
                updated_at = excluded.updated_at
            """,
            (airtable_id, local_table, local_id, dt.datetime.utcnow().isoformat()),
        )

    # --- Sync handlers ----------------------------------------------------
    def sync_prospects(self, records: Iterable[dict]) -> None:
        for record in records:
            fields = record.get("fields", {})
            name = fields.get("Name")
            if not name:
                continue
            stage = self.normalize_stage(fields.get("Frazer Stage"))
            email = fields.get("Email")
            owner = fields.get("Owner") or fields.get("Next Action Owner")
            source = fields.get("Primary Channel")
            last_touch = fields.get("Last Touch")
            lead_id = self._lookup_sync(record["id"], "leads")
            if self.dry_run:
                logging.info("[DRY RUN] Would sync lead %s (%s)", name, record["id"])
                continue
            if lead_id:
                self.conn.execute(
                    """
                    UPDATE leads
                    SET name = ?, email = ?, stage = ?, owner = ?, source = ?, last_touch = ?
                    WHERE id = ?
                    """,
                    (name, email, stage, owner, source, last_touch, lead_id),
                )
            else:
                cursor = self.conn.execute(
                    """
                    INSERT INTO leads (name, email, stage, owner, source, last_touch)
                    VALUES (?, ?, ?, ?, ?, ?)
                    """,
                    (name, email, stage, owner, source, last_touch),
                )
                lead_id = cursor.lastrowid
                self._upsert_sync(record["id"], "leads", lead_id)
            next_action = fields.get("Next Action")
            if next_action:
                task_key = f"{record['id']}:next_action"
                status = "completed" if fields.get("Next Action Status") == "Done" else "pending"
                due_date = fields.get("Next Action Date")
                self.upsert_task(
                    task_key,
                    title=f"{name} – {next_action}",
                    status=status,
                    priority=STAGE_PRIORITY.get(stage, "medium"),
                    assigned_to=owner,
                    due_date=due_date,
                )

    def sync_touchpoints(self, records: Iterable[dict]) -> None:
        for record in records:
            fields = record.get("fields", {})
            description = fields.get("Touchpoint Type") or "Touchpoint"
            details = fields.get("Notes")
            agent_name = fields.get("Owner")
            timestamp = fields.get("Timestamp") or fields.get("Created")
            airtable_id = record.get("id")
            if not airtable_id:
                continue
            log_id = self._lookup_sync(airtable_id, "activity_log")
            if self.dry_run:
                logging.info("[DRY RUN] Would sync touchpoint %s", airtable_id)
                continue
            if log_id:
                self.conn.execute(
                    """
                    UPDATE activity_log
                    SET agent_name = ?, description = ?, details = ?, timestamp = ?
                    WHERE id = ?
                    """,
                    (agent_name, description, details, timestamp, log_id),
                )
            else:
                cursor = self.conn.execute(
                    """
                    INSERT INTO activity_log (agent_name, description, details, timestamp)
                    VALUES (?, ?, ?, ?)
                    """,
                    (agent_name, description, details, timestamp),
                )
                self._upsert_sync(airtable_id, "activity_log", cursor.lastrowid)

    def sync_followups(self, records: Iterable[dict]) -> None:
        for record in records:
            fields = record.get("fields", {})
            reminder_time = fields.get("Reminder Date") or fields.get("Reminder DateTime")
            if not reminder_time:
                continue
            title = fields.get("Reminder Template") or "Frazer Follow-Up"
            description = fields.get("Notes")
            lead_name = fields.get("Prospect Name")
            lead_id = None
            if lead_name:
                lead_id = self.lookup_lead_id_by_name(lead_name)
            state_key = record["id"]
            if self.dry_run:
                logging.info("[DRY RUN] Would sync reminder %s", state_key)
                continue
            reminder_id = self._lookup_sync(state_key, "reminders")
            if reminder_id:
                self.conn.execute(
                    """
                    UPDATE reminders
                    SET lead_id = ?, reminder_datetime = ?, title = ?, description = ?
                    WHERE id = ?
                    """,
                    (lead_id, reminder_time, title, description, reminder_id),
                )
            else:
                cursor = self.conn.execute(
                    """
                    INSERT INTO reminders (lead_id, reminder_datetime, title, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (lead_id, reminder_time, title, description),
                )
                self._upsert_sync(state_key, "reminders", cursor.lastrowid)

    def sync_coaching(self, records: Iterable[dict]) -> None:
        for record in records:
            fields = record.get("fields", {})
            suggestion = fields.get("AI Suggestion")
            if not suggestion:
                continue
            lead_name = fields.get("Prospect Name") or fields.get("Prospect Lookup")
            stage = self.normalize_stage(fields.get("Bottleneck Stage"))
            content = f"[{stage}] {suggestion}"
            note_key = record["id"]
            requires_followup = fields.get("Human Decision") == "Needs Review"
            reminder_time = fields.get("Next Review")
            if self.dry_run:
                logging.info("[DRY RUN] Would sync coaching note %s", note_key)
                continue
            note_id = self._lookup_sync(note_key, "quick_notes")
            if note_id:
                self.conn.execute(
                    """
                    UPDATE quick_notes
                    SET content = ?, raw_content = ?, note_type = ?, priority = ?, lead_name = ?, status = ?
                    WHERE id = ?
                    """,
                    (
                        content,
                        suggestion,
                        "coaching",
                        STAGE_PRIORITY.get(stage, "medium"),
                        lead_name,
                        "assigned" if requires_followup else "auto_assigned",
                        note_id,
                    ),
                )
            else:
                cursor = self.conn.execute(
                    """
                    INSERT INTO quick_notes (
                        content, raw_content, note_type, priority, requires_disambiguation,
                        lead_name, status
                    )
                    VALUES (?, ?, 'coaching', ?, ?, ?, ?)
                    """,
                    (
                        content,
                        suggestion,
                        STAGE_PRIORITY.get(stage, "medium"),
                        bool(requires_followup),
                        lead_name,
                        "assigned" if requires_followup else "auto_assigned",
                    ),
                )
                note_id = cursor.lastrowid
                self._upsert_sync(note_key, "quick_notes", note_id)
            if reminder_time and not self.dry_run:
                reminder_key = f"{note_key}:reminder"
                reminder_id = self._lookup_sync(reminder_key, "reminders")
                title = f"Coaching follow-up: {lead_name or 'Prospect'}"
                if reminder_id:
                    self.conn.execute(
                        "UPDATE reminders SET reminder_datetime = ?, title = ? WHERE id = ?",
                        (reminder_time, title, reminder_id),
                    )
                else:
                    cursor = self.conn.execute(
                        "INSERT INTO reminders (note_id, reminder_datetime, title, description) VALUES (?, ?, ?, ?)",
                        (note_id, reminder_time, title, suggestion),
                    )
                    self._upsert_sync(reminder_key, "reminders", cursor.lastrowid)

    def upsert_task(
        self,
        airtable_id: str,
        title: str,
        status: str,
        priority: str,
        assigned_to: Optional[str],
        due_date: Optional[str],
    ) -> None:
        if self.dry_run:
            logging.info("[DRY RUN] Would sync task %s", airtable_id)
            return
        task_id = self._lookup_sync(airtable_id, "tasks")
        if task_id:
            self.conn.execute(
                """
                UPDATE tasks
                SET title = ?, status = ?, priority = ?, assigned_to = ?, due_date = ?
                WHERE id = ?
                """,
                (title, status, priority, assigned_to, due_date, task_id),
            )
        else:
            cursor = self.conn.execute(
                """
                INSERT INTO tasks (title, status, priority, assigned_to, due_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (title, status, priority, assigned_to, due_date),
            )
            self._upsert_sync(airtable_id, "tasks", cursor.lastrowid)

    # --- Utility methods --------------------------------------------------
    def normalize_stage(self, stage: Optional[str]) -> str:
        if not stage:
            return "Lead"
        stage = stage.strip()
        if stage in FRAZER_STAGE_ORDER:
            return stage
        # attempt loose matching
        for canonical in FRAZER_STAGE_ORDER:
            if stage.lower() in canonical.lower() or canonical.lower() in stage.lower():
                return canonical
        return "Lead"

    def lookup_lead_id_by_name(self, name: str) -> Optional[int]:
        cursor = self.conn.execute("SELECT id FROM leads WHERE name = ?", (name,))
        row = cursor.fetchone()
        return int(row[0]) if row else None

    def sync(self, tables: Optional[List[str]] = None) -> None:
        config: Dict[str, Dict[str, Optional[str]]] = {
            "prospects": {
                "table": os.getenv("AIRTABLE_PROSPECT_TABLE", "Prospects"),
                "view": os.getenv("AIRTABLE_PROSPECT_VIEW", "Frazer Pipeline"),
            },
            "touchpoints": {
                "table": os.getenv("AIRTABLE_TOUCHPOINT_TABLE", "Pipeline Touchpoints"),
                "view": os.getenv("AIRTABLE_TOUCHPOINT_VIEW", "All"),
            },
            "followups": {
                "table": os.getenv("AIRTABLE_FOLLOWUP_TABLE", "Follow-Up Automations"),
                "view": os.getenv("AIRTABLE_FOLLOWUP_VIEW", "Active"),
            },
            "coaching": {
                "table": os.getenv("AIRTABLE_COACHING_TABLE", "AI Coaching Insights"),
                "view": os.getenv("AIRTABLE_COACHING_VIEW", "Needs Attention"),
            },
        }
        tables_to_sync = tables or list(config.keys())
        for key in tables_to_sync:
            if key not in config:
                logging.warning("Unknown table key '%s' - skipping", key)
                continue
            table_name = config[key]["table"]
            view_name = config[key]["view"]
            logging.info("Syncing Airtable table '%s' (view=%s) → %s", table_name, view_name, key)
            records = self.fetch_records(table_name, view=view_name)
            handler = getattr(self, f"sync_{key}")
            handler(records)
        if not self.dry_run:
            self.conn.commit()

    def close(self) -> None:
        self.conn.close()


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sync Airtable data into the Flowstate-AI SQLite sandbox")
    parser.add_argument(
        "--tables",
        nargs="*",
        choices=["prospects", "touchpoints", "followups", "coaching"],
        help="Optional subset of tables to sync",
    )
    parser.add_argument("--dry-run", action="store_true", help="Print actions without modifying the database")
    return parser.parse_args()


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="[%(asctime)s] %(levelname)s %(message)s")
    args = parse_args()
    api_key = os.environ.get("AIRTABLE_API_KEY")
    base_id = os.environ.get("AIRTABLE_BASE_ID")
    if not api_key or not base_id:
        raise SystemExit("AIRTABLE_API_KEY and AIRTABLE_BASE_ID must be set in the environment")
    bridge = AirtableBridge(api_key, base_id, DB_PATH, dry_run=args.dry_run)
    try:
        bridge.sync(tables=args.tables)
    finally:
        bridge.close()


if __name__ == "__main__":
    main()
