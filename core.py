from contextlib import closing

import db


def clean_topic(topic: str) -> str:
    """Normalise topics so 'OS', 'os ' and 'Os' all match."""
    return topic.strip().lower()


def add_card(topic: str, question: str, answer: str) -> int:
    """Insert a card and return how many cards the topic now has."""
    topic = clean_topic(topic)
    if not topic or not question.strip() or not answer.strip():
        raise ValueError("Topic, question and answer cannot be empty.")
    with closing(db.get_conn()) as conn, conn:
        conn.execute(
            "INSERT INTO flashcards (topic, question, answer) VALUES (?, ?, ?)",
            (topic, question.strip(), answer.strip()),
        )
        return conn.execute(
            "SELECT COUNT(*) FROM flashcards WHERE topic = ?", (topic,)
        ).fetchone()[0]


def random_card(topic: str) -> dict | None:
    """Return one random card for the topic, or None if there are none."""
    with closing(db.get_conn()) as conn:
        row = conn.execute(
            "SELECT question, answer FROM flashcards "
            "WHERE topic = ? ORDER BY RANDOM() LIMIT 1",
            (clean_topic(topic),),
        ).fetchone()
    return dict(row) if row else None


def list_topics() -> list[str]:
    with closing(db.get_conn()) as conn:
        rows = conn.execute(
            "SELECT DISTINCT topic FROM flashcards ORDER BY topic"
        ).fetchall()
    return [r["topic"] for r in rows]