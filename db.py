import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

# Anchor the DB file next to this script, so it doesn't depend on
# which folder you launched Python from.
DB_PATH = Path(__file__).parent / "cards.db"


@contextmanager
def get_conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        with conn:
            yield conn
    finally:
        conn.close()


def init_db() -> None:
    with get_conn() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                topic TEXT NOT NULL,
                question TEXT NOT NULL,
                answer TEXT NOT NULL
            )
            """
        )
        
