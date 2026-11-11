import json
import sqlite3
from datetime import datetime

import numpy as np

DB_FILE = "faces.db"
MIN_SECONDS_BEFORE_CHECKOUT = 60   # blocks an accidental double tap


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    """Creates the tables the first time. Safe to run many times."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS face_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                encoding TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS attendance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                work_date TEXT NOT NULL,
                check_in TEXT NOT NULL,
                check_out TEXT
            )
        """)


def save_samples(employee_id, encodings):
    """Replaces any old samples for this employee with the new ones."""
    rows = [(employee_id, json.dumps([float(x) for x in e])) for e in encodings]
    with get_connection() as conn:
        conn.execute("DELETE FROM face_samples WHERE employee_id = ?", (employee_id,))
        conn.executemany(
            "INSERT INTO face_samples (employee_id, encoding) VALUES (?, ?)", rows
        )


def get_samples(employee_id):
    """Returns the saved face numbers for one employee as a list."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT encoding FROM face_samples WHERE employee_id = ?", (employee_id,)
        ).fetchall()
    return [np.array(json.loads(r[0])) for r in rows]


def mark_attendance(employee_id):
    """First call today = check-in, next call = check-out."""
    now = datetime.now()
    today = now.strftime("%Y-%m-%d")
    stamp = now.strftime("%H:%M:%S")

    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, check_in, check_out FROM attendance "
            "WHERE employee_id = ? AND work_date = ?",
            (employee_id, today),
        ).fetchone()

        if row is None:
            conn.execute(
                "INSERT INTO attendance (employee_id, work_date, check_in) VALUES (?, ?, ?)",
                (employee_id, today, stamp),
            )
            return {"action": "check_in", "time": stamp}

        if row[2] is None:
            check_in_time = datetime.strptime(today + " " + row[1], "%Y-%m-%d %H:%M:%S")
            if (now - check_in_time).total_seconds() < MIN_SECONDS_BEFORE_CHECKOUT:
                return {"action": "too_soon", "time": row[1]}
            conn.execute("UPDATE attendance SET check_out = ? WHERE id = ?", (stamp, row[0]))
            return {"action": "check_out", "time": stamp}

        return {"action": "already_done", "time": row[2]}


def get_attendance(work_date):
    """All attendance rows for one day."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT employee_id, check_in, check_out FROM attendance "
            "WHERE work_date = ? ORDER BY check_in",
            (work_date,),
        ).fetchall()
    return [{"employee_id": r[0], "check_in": r[1], "check_out": r[2]} for r in rows]