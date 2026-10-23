import asyncio

import pytest
from mcp import Client

import db
import server


@pytest.fixture(autouse=True)
def fresh_db(tmp_path, monkeypatch):
    """Each test runs against its own empty database."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()


def call(tool: str, args: dict) -> str:
    async def run():
        async with Client(server.mcp) as client:
            return await client.call_tool(tool, args)

    return str(asyncio.run(run()))


def test_add_and_quiz():
    assert "Saved" in call(
        "add_flashcard",
        {"topic": "os", "question": "What is a process?", "answer": "A running program"},
    )
    assert "What is a process?" in call("quiz_me", {"topic": "os"})


def test_topic_is_normalised():
    call("add_flashcard", {"topic": "  OS ", "question": "Q1", "answer": "A1"})
    assert "Q1" in call("quiz_me", {"topic": "os"})


def test_empty_input_rejected():
    assert "cannot be empty" in call(
        "add_flashcard", {"topic": "os", "question": "  ", "answer": "A"}
    )


def test_missing_topic_gives_error():
    assert "No cards found" in call("quiz_me", {"topic": "chemistry"})


def test_list_topics():
    call("add_flashcard", {"topic": "networking", "question": "Q", "answer": "A"})
    assert "networking" in call("list_topics", {})


def test_connection_closes_after_exception():
    with pytest.raises(RuntimeError, match="expected failure"):
        with db.get_conn() as conn:
            raise RuntimeError("expected failure")

    with pytest.raises(Exception):
        conn.execute("SELECT 1")
