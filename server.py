
import os

from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

import db


mcp = MCPServer("study-buddy")
db.init_db()


def _clean(topic: str) -> str:
    """Normalize topics so OS, os and Os match."""
    return topic.strip().lower()


@mcp.tool()
def add_flashcard(topic: str, question: str, answer: str) -> str:
    """Save a flashcard under a topic."""
    topic = _clean(topic)

    if not topic or not question.strip() or not answer.strip():
        return "Topic, question and answer cannot be empty."

    with db.get_conn() as conn:
        conn.execute(
            """
            INSERT INTO flashcards (topic, question, answer)
            VALUES (?, ?, ?)
            """,
            (topic, question.strip(), answer.strip()),
        )

        count = conn.execute(
            "SELECT COUNT(*) FROM flashcards WHERE topic = ?",
            (topic,),
        ).fetchone()[0]

    return f"Saved. You now have {count} card(s) on {topic}."


@mcp.tool()
def quiz_me(topic: str) -> dict:
    """Return one random flashcard question and answer."""
    topic = _clean(topic)

    with db.get_conn() as conn:
        row = conn.execute(
            """
            SELECT question, answer
            FROM flashcards
            WHERE topic = ?
            ORDER BY RANDOM()
            LIMIT 1
            """,
            (topic,),
        ).fetchone()

    if row is None:
        return {"error": f"No cards found for '{topic}'. Add some first."}

    return {
        "question": row["question"],
        "answer": row["answer"],
    }


@mcp.tool()
def list_topics() -> list[str]:
    """List every topic that has at least one flashcard."""
    with db.get_conn() as conn:
        rows = conn.execute(
            """
            SELECT DISTINCT topic
            FROM flashcards
            ORDER BY topic
            """
        ).fetchall()

    return [row["topic"] for row in rows]


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME")

    options = {
        "host": "0.0.0.0",
        "port": port,
    }

    if render_host:
        options["transport_security"] = TransportSecuritySettings(
            allowed_hosts=[
                render_host,
                f"{render_host}:*",
            ]
        )

    mcp.run(
        transport="streamable-http",
        **options,
    )
