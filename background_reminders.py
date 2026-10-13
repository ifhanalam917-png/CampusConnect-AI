
import time
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from winotify import Notification, audio

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "campusconnect.db"

CHECK_INTERVAL = 30  # Check every 30 seconds


def send_notification(title, message):
    try:
        notification = Notification(
            app_id="CampusConnect AI",
            title=title,
            msg=message
        )

        notification.set_audio(
            audio.Default,
            loop=False
        )

        notification.show()
        print(f"Notification sent: {title}")

    except Exception as error:
        print(f"Notification error: {error}")


def check_reminders():
    now = datetime.now()

    with sqlite3.connect(DB_PATH, timeout=10) as connection:
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

        reminders = connection.execute("""
            SELECT id, title, due_at, notes,
                   advance_sent, due_sent
            FROM reminders
            ORDER BY due_at
        """).fetchall()

        for reminder in reminders:
            (
                reminder_id,
                title,
                due_at,
                notes,
                advance_sent,
                due_sent
            ) = reminder

            try:
                deadline = datetime.fromisoformat(due_at)
            except ValueError:
                print(f"Invalid deadline for reminder {reminder_id}")
                continue

            advance_time = deadline - timedelta(days=1)

            # Send the one-day-before alert once.
            if not advance_sent and advance_time <= now < deadline:
                send_notification(
                    "CampusConnect AI — Upcoming Deadline",
                    f"{title} is due within 24 hours."
                )

                connection.execute("""
                    UPDATE reminders
                    SET advance_sent = 1
                    WHERE id = ?
                """, (reminder_id,))

            # Send the deadline alert once.
            if not due_sent and now >= deadline:
                send_notification(
                    "CampusConnect AI — Deadline Reached",
                    f"{title} is due now. Check your task!"
                )

                connection.execute("""
                    UPDATE reminders
                    SET due_sent = 1
                    WHERE id = ?
                """, (reminder_id,))

        connection.commit()


if __name__ == "__main__":
    print("CampusConnect AI background reminders started.")
    print("Keep this terminal open while reminders are active.")

    while True:
        try:
            check_reminders()
        except Exception as error:
            print(f"Reminder checker error: {error}")

        time.sleep(CHECK_INTERVAL)