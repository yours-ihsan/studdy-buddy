# Study Buddy MCP

A self-hosted [MCP](https://modelcontextprotocol.io) server that lets an AI
assistant create flashcards and quiz you on them. Built for the Amazon
developer hackathon, **Alexa+ track** (simulated-experience path).

## What it does

The server exposes three tools over **Streamable HTTP** (it negotiates MCP
spec 2025-11-25):

- `add_flashcard(topic, question, answer)` saves a card
- `quiz_me(topic)` returns a random card for a topic
- `list_topics()` lists topics that have cards

Cards are stored in SQLite, so they persist across restarts. Topics are
normalised, so "OS", "os " and "Os" all match.

A simulated Alexa+ web app (`simulator/`) connects to the server with the MCP
SDK's `Client` and calls these tools. It has a flip-card quiz view, voice input
and read-aloud (Chrome/Edge), accuracy and streak tracking, and an
"MCP activity" panel that shows each real tool call.

## Architecture

```
Browser (simulator UI)  ->  FastAPI (port 8001)  ->  MCP server (port 8000)  ->  SQLite
                            uses mcp.Client          uses MCPServer            cards.db
```

## Run it

Requires Python 3.10+.

**Windows (PowerShell)**
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```

**macOS / Linux**
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python server.py
```

The MCP server listens at `http://127.0.0.1:8000/mcp`.

In a **second terminal** (with the venv active):
```
python simulator/app.py
```
Then open http://127.0.0.1:8001, add a card, and click its topic to start a quiz.

To test the server directly: `npx @modelcontextprotocol/inspector`, choose
Streamable HTTP, and enter `http://127.0.0.1:8000/mcp`.

## Project layout

```
server.py            MCP server and tool definitions
db.py                SQLite connection and schema
simulator/app.py     FastAPI backend that calls the MCP server
simulator/index.html Simulated Alexa+ chat and quiz UI
```

## License

MIT