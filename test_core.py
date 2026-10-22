import pytest

import core
import db


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test gets a fresh empty database."""
    monkeypatch.setattr(db, "DB_PATH", tmp_path / "test.db")
    db.init_db()


def test_add_card_counts_per_topic():
    assert core.add_card("os", "What is a process?", "A running program") == 1
    assert core.add_card("os", "What is a thread?", "A unit of execution") == 2


def test_topics_are_normalised():
    core.add_card("  Operating Systems ", "Q", "A")
    assert core.list_topics() == ["operating systems"]
    assert core.random_card("OPERATING SYSTEMS") is not None


def test_empty_input_rejected():
    with pytest.raises(ValueError):
        core.add_card("os", "   ", "answer")


def test_missing_topic_returns_none():
    assert core.random_card("chemistry") is None


def test_list_topics_sorted_and_unique():
    core.add_card("b", "Q1", "A1")
    core.add_card("a", "Q2", "A2")
    core.add_card("a", "Q3", "A3")
    assert core.list_topics() == ["a", "b"]