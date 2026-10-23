import asyncio
import importlib
from types import SimpleNamespace

simulator = importlib.import_module("simulator.app")


class FakeClient:
    calls = []
    result = SimpleNamespace(structured_content={"result": "Saved card"}, content=[])
    error = None
    result_error = False

    def __init__(self, url):
        self.url = url

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return False

    async def call_tool(self, tool, args):
        self.calls.append((tool, args))
        if self.error:
            raise self.error
        return SimpleNamespace(
            structured_content=self.result.structured_content,
            content=self.result.content,
            is_error=self.result_error,
        )


def setup_function():
    simulator.activity.clear()
    FakeClient.calls.clear()
    FakeClient.error = None
    FakeClient.result_error = False


def test_activity_records_actual_tool_and_arguments(monkeypatch):
    monkeypatch.setattr(simulator, "Client", FakeClient)
    response = asyncio.run(simulator.chat(simulator.Chat(message="add OS | Q | A")))
    record = simulator.get_activity()[0]

    assert response["reply"] == "Saved card"
    assert FakeClient.calls == [("add_flashcard", {"topic": "OS", "question": "Q", "answer": "A"})]
    assert record["tool"] == FakeClient.calls[0][0]
    assert record["arguments"] == FakeClient.calls[0][1]
    assert record["status"] == "success"
    assert record["summary"] == "Saved card"


def test_local_answer_lookup_is_not_recorded_as_mcp_call(monkeypatch):
    monkeypatch.setattr(simulator, "Client", FakeClient)
    simulator.last_answer = "Previously returned answer"
    response = asyncio.run(simulator.chat(simulator.Chat(message="answer")))

    assert response["reply"] == "Previously returned answer"
    assert FakeClient.calls == []
    assert list(simulator.activity) == []


def test_failed_mcp_call_is_recorded(monkeypatch):
    monkeypatch.setattr(simulator, "Client", FakeClient)
    FakeClient.error = RuntimeError("server unavailable")
    asyncio.run(simulator.chat(simulator.Chat(message="topics")))
    record = simulator.get_activity()[0]

    assert record["tool"] == FakeClient.calls[0][0] == "list_topics"
    assert record["arguments"] == FakeClient.calls[0][1] == {}
    assert record["status"] == "failure"
    assert "server unavailable" in record["summary"]


def test_mcp_tool_error_result_is_recorded_as_failure(monkeypatch):
    monkeypatch.setattr(simulator, "Client", FakeClient)
    FakeClient.result_error = True
    asyncio.run(simulator.chat(simulator.Chat(message="topics")))
    record = simulator.get_activity()[0]

    assert record["tool"] == "list_topics"
    assert record["status"] == "failure"
