"""Database helpers for PantryTrack.

PantryTrack stores everything in a single SQLite file so that a small
business can run it on any laptop without installing a database server.
"""

from __future__ import annotations

import os
import sqlite3
from pathlib import Path

DEFAULT_DB_ENV = "PANTRYTRACK_DB"
DEFAULT_DB_NAME = "pantrytrack.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS items (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    name           TEXT    NOT NULL UNIQUE COLLATE NOCASE,
    category       TEXT,
    unit           TEXT    NOT NULL,
    quantity       REAL    NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    reorder_level  REAL    NOT NULL DEFAULT 0 CHECK (reorder_level >= 0),
    unit_cost      REAL    NOT NULL DEFAULT 0 CHECK (unit_cost >= 0),
    supplier       TEXT,
    created_at     TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS movements (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id     INTEGER NOT NULL REFERENCES items(id) ON DELETE CASCADE,
    kind        TEXT    NOT NULL CHECK (kind IN ('in', 'use', 'waste', 'adjust')),
    quantity    REAL    NOT NULL,
    unit_cost   REAL    NOT NULL DEFAULT 0,
    note        TEXT,
    created_at  TEXT    NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_movements_item ON movements(item_id);
CREATE INDEX IF NOT EXISTS idx_movements_created ON movements(created_at);
"""


def default_db_path() -> Path:
    """Return the database path from the environment or the current folder."""
    return Path(os.environ.get(DEFAULT_DB_ENV, DEFAULT_DB_NAME))


def connect(path: str | os.PathLike | None = None) -> sqlite3.Connection:
    """Open (and if needed create) the PantryTrack database.

    Passing ``":memory:"`` creates a temporary in-memory database, which is
    what the test-suite uses.
    """
    db_path = str(path) if path is not None else str(default_db_path())
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    init_schema(conn)
    return conn


def init_schema(conn: sqlite3.Connection) -> None:
    """Create the tables if they do not exist yet (safe to call repeatedly)."""
    conn.executescript(SCHEMA)
    conn.commit()
