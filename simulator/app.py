import json
from pathlib import Path

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse
from mcp import Client
from pydantic import BaseModel

MCP_URL = "http://127.0.0.1:8000/mcp"
HERE = Path(__file__).parent

app = FastAPI()
last_answer = ""


class Chat(BaseModel):
    message: str


def unwrap(result):
    """Pull a plain Python value out of an MCP tool result."""
    data = getattr(result, "structured_content", None) or getattr(
        result, "structuredContent", None
    )
    if isinstance(data, dict) and list(data) == ["result"]:
        return data["result"]
    if data is not None:
        return data
    for block in getattr(result, "content", None) or []:
        text = getattr(block, "text", None)
        if text is not None:
            try:
                return json.loads(text)
            except ValueError:
                return text
    return str(result)


async def call(tool: str, args: dict):
    async with Client(MCP_URL) as client:
        return unwrap(await client.call_tool(tool, args))


@app.get("/")
def index():
    return FileResponse(HERE / "index.html")


@app.post("/chat")
async def chat(body: Chat):
    global last_answer
    msg = body.message.strip()
    low = msg.lower()
    try:
        if low.startswith("quiz me on "):
            out = await call("quiz_me", {"topic": msg[11:]})
            if isinstance(out, dict) and "question" in out:
                last_answer = out["answer"]
                return {"reply": out["question"]}
            return {"reply": out.get("error", str(out)) if isinstance(out, dict) else str(out)}
        if low in ("answer", "show answer"):
            return {"reply": last_answer or "Ask for a quiz first."}
        if low.startswith("add "):
            parts = [p.strip() for p in msg[4:].split("|")]
            if len(parts) != 3:
                return {"reply": "Use: add topic | question | answer"}
            out = await call(
                "add_flashcard",
                {"topic": parts[0], "question": parts[1], "answer": parts[2]},
            )
            return {"reply": str(out)}
        if "topics" in low:
            out = await call("list_topics", {})
            return {"reply": ", ".join(out) if isinstance(out, list) and out else "No topics yet."}
        return {"reply": "Try: add os | question | answer, quiz me on os, answer, topics"}
    except Exception as exc:
        return {"reply": f"Could not reach the MCP server: {exc}"}


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)