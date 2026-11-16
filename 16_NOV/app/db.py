import sqlite3
import uuid
from contextlib import contextmanager
from datetime import datetime, timezone

from app import config

# The CHECK rules let the database itself reject bad data,
# even if some code forgets to validate.
SCHEMA = """
CREATE TABLE IF NOT EXISTS trips (
    trip_id     TEXT PRIMARY KEY,
    employee_id TEXT NOT NULL,
    destination TEXT NOT NULL,
    start_date  TEXT NOT NULL,          -- stored as 'YYYY-MM-DD'
    end_date    TEXT NOT NULL,
    purpose     TEXT NOT NULL,
    status      TEXT NOT NULL DEFAULT 'planned'
                CHECK (status IN ('planned', 'completed', 'cancelled')),
    created_at  TEXT NOT NULL,
    CHECK (end_date >= start_date)
);
CREATE INDEX IF NOT EXISTS idx_trips_employee ON trips(employee_id);
"""


@contextmanager
def get_connection():
    """Open a connection, commit if all went well, and ALWAYS close it."""
    conn = sqlite3.connect(config.SQLITE_PATH)
    conn.row_factory = sqlite3.Row      # rows behave like dicts: row["destination"]
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        conn.executescript(SCHEMA)


def create_trip(employee_id: str, destination: str, start_date: str,
                end_date: str, purpose: str, status: str = "planned") -> dict:
    trip_id = "TRIP-" + uuid.uuid4().hex[:8].upper()          # e.g. TRIP-3F9A1C2B
    created_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with get_connection() as conn:
        conn.execute(
            """INSERT INTO trips (trip_id, employee_id, destination, start_date,
                                  end_date, purpose, status, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (trip_id, employee_id, destination, start_date,
             end_date, purpose, status, created_at),
        )
    return get_trip(trip_id)


def get_trip(trip_id: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM trips WHERE trip_id = ?", (trip_id,)
        ).fetchone()
    return dict(row) if row else None


def list_all_trips() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM trips ORDER BY created_at DESC").fetchall()
    return [dict(r) for r in rows]


def list_trips(employee_id: str) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM trips WHERE employee_id = ? ORDER BY start_date",
            (employee_id,),
        ).fetchall()
    return [dict(r) for r in rows]
