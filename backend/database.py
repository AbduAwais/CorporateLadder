import sqlite3
import os

DB_PATH = os.environ.get("DB_PATH", os.path.join(os.path.dirname(__file__), "leaderboard.db"))


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db() -> None:
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS leaderboard (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT    NOT NULL COLLATE NOCASE UNIQUE,
            score      INTEGER NOT NULL,
            rank       TEXT,
            words      INTEGER,
            streak     INTEGER,
            created_at TEXT    DEFAULT (datetime('now')),
            updated_at TEXT    DEFAULT (datetime('now'))
        )
    """)
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_leaderboard_score
        ON leaderboard(score DESC)
    """)
    conn.commit()
    conn.close()
