from mcp.server import MCPServer

import core
import db

mcp = MCPServer("study-buddy")
db.init_db()


@mcp.tool()
def add_flashcard(topic: str, question: str, answer: str) -> str:
    """Save a flashcard under a topic, e.g. 'operating systems'."""
    try:
        count = core.add_card(topic, question, answer)
    except ValueError as exc:
        return str(exc)
    return f"Saved. You now have {count} card(s) on {core.clean_topic(topic)}."


@mcp.tool()
def quiz_me(topic: str) -> dict:
    """Return one random flashcard (question and answer) for a topic."""
    card = core.random_card(topic)
    if card is None:
        return {"error": f"No cards found for '{core.clean_topic(topic)}'. Add some first."}
    return card


@mcp.tool()
def list_topics() -> list[str]:
    """List every topic that has at least one flashcard."""
    return core.list_topics()


if __name__ == "__main__":
    mcp.run(transport="streamable-http")