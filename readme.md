# Study Buddy MCP

An MCP server (Streamable HTTP) that lets an AI assistant create and quiz
you on flashcards. Built for the Amazon developer hackathon, Alexa+ track.

## Tools
- `add_flashcard(topic, question, answer)`
- `quiz_me(topic)`
- `list_topics()`

## Run it
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python server.py
```
The server listens at `http://127.0.0.1:8000/mcp`.
Test it with: `npx @modelcontextprotocol/inspector`

## License
MIT