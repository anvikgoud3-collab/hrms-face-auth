import json
import sqlite3
import numpy as np

DB_FILE = "faces.db"


def get_connection():
    return sqlite3.connect(DB_FILE)


def init_db():
    """Creates the table the first time. Safe to run many times."""
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS face_samples (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                employee_id TEXT NOT NULL,
                encoding TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
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