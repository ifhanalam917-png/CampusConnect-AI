

import sqlite3
from pathlib import Path

# Always use the database inside the project folder.
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "campusconnect.db"


def initialize_reminders():
    """Create the reminder table without changing existing tables."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                due_at TEXT NOT NULL,
                notes TEXT DEFAULT '',
                advance_sent INTEGER NOT NULL DEFAULT 0,
                due_sent INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        connection.commit()


def add_reminder(title, due_at, notes=""):
    """Save a new reminder."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute("""
            INSERT INTO reminders (title, due_at, notes)
            VALUES (?, ?, ?)
        """, (title.strip(), due_at, notes.strip()))
        connection.commit()


def get_reminders():
    """Return reminders in deadline order."""
    with sqlite3.connect(DB_PATH) as connection:
        return connection.execute("""
            SELECT id, title, due_at, notes, advance_sent, due_sent
            FROM reminders
            ORDER BY due_at
        """).fetchall()


def mark_reminder_sent(reminder_id, alert_type):
    """Record an alert to avoid repeatedly sending it."""
    if alert_type not in ("advance_sent", "due_sent"):
        raise ValueError("Unknown reminder alert type.")

    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            f"UPDATE reminders SET {alert_type} = 1 WHERE id = ?",
            (reminder_id,)
        )
        connection.commit()


def delete_reminder(reminder_id):
    """Delete one reminder by its ID."""
    with sqlite3.connect(DB_PATH) as connection:
        connection.execute(
            "DELETE FROM reminders WHERE id = ?",
            (reminder_id,)
        )
        connection.commit()
