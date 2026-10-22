"""Tests for the MCP surface of ``notes_mcp.server`` (tools first, then
resources and prompts as the implementation grows).

These use the SDK's own recommended test pattern: connect an ``mcp.Client``
**in-process** to the ``MCPServer`` object itself (``Client(mcp)``). No
subprocess, no port, no stdio — but every call still traverses the real
protocol layer (validation, capabilities, JSON-RPC dispatch), so what these
tests pin is what a real host experiences. See docs/04-testing.md.

The environment variable ``NOTES_DB_PATH`` is pointed at a fresh
``tmp_path`` database in a fixture so tests are deterministic and can never
touch the demo database in ``data/``.
"""

import anyio
import pytest
from mcp import Client
from mcp.types import TextContent

from notes_mcp import db
from notes_mcp.server import mcp


@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DB_PATH", str(tmp_path / "server-test.db"))
    db.init_db()


def _run(coro_fn):
    """Sync pytest entry into the coroutine body (anyio ships with the SDK).

    Each test's ``body()`` opens its OWN ``async with Client(mcp)`` block —
    that context manager IS the connection lifecycle (connect at enter,
    disconnect at exit), so returning from inside it is the natural shape.
    """
    return anyio.run(coro_fn)


def _text(result) -> str:
    """Concatenate the TextContent blocks of a CallToolResult."""
    return "\n".join(
        block.text for block in result.content if isinstance(block, TextContent)
    )


def test_list_tools_names(fresh_db):
    async def body():
        async with Client(mcp) as client:
            result = await client.list_tools()
        return {tool.name for tool in result.tools}

    assert _run(body) == {"add_note", "search_notes", "update_note", "delete_note"}


def test_add_note_structured_output(fresh_db):
    """Pydantic return => structured_content (for code) + text (for the model)."""

    async def body():
        async with Client(mcp) as client:
            result = await client.call_tool(
                "add_note",
                {"title": "Structured", "content": "Body X", "tags": ["x", "y"]},
            )
        return result

    result = _run(body)
    assert result.is_error is False
    structured = result.structured_content
    assert structured["title"] == "Structured"
    assert structured["content"] == "Body X"
    assert structured["tags"] == ["x", "y"]
    assert structured["id"] > 0
    # the human/model-readable half mirrors the same data as JSON text
    assert "Structured" in _text(result)


def test_add_note_defaults_to_no_tags(fresh_db):
    async def body():
        async with Client(mcp) as client:
            result = await client.call_tool("add_note", {"title": "T", "content": "C"})
        return result

    assert _run(body).structured_content["tags"] == []


def test_search_notes_format(fresh_db):
    async def body():
        async with Client(mcp) as client:
            result = await client.call_tool("search_notes", {"query": "mcp"})
        return result

    text = _text(_run(body))
    assert "matching " in text  # the 'Found N note(s) matching' header
    assert "- #" in text  # one bullet per hit


def test_search_empty_query_lists_recent(fresh_db):
    """Empty query == 'list my newest notes', not an error (Review Focus #5)."""

    async def body():
        async with Client(mcp) as client:
            result = await client.call_tool("search_notes", {"query": ""})
        return result

    result = _run(body)
    assert result.is_error is False
    assert "- #" in _text(result)


def test_delete_missing_note_is_error(fresh_db):
    """Expected failures are *data*, not crashes: is_error=True + readable text."""

    async def body():
        async with Client(mcp) as client:
            return await client.call_tool("delete_note", {"note_id": 424242})

    result = _run(body)
    assert result.is_error is True
    assert "not found" in _text(result)


def test_update_missing_note_is_error(fresh_db):
    async def body():
        async with Client(mcp) as client:
            return await client.call_tool(
                "update_note", {"note_id": 424242, "title": "whoops"}
            )

    result = _run(body)
    assert result.is_error is True
    assert "not found" in _text(result)


def test_update_roundtrip_through_tool(fresh_db):
    async def body():
        added = db.add_note("Old title", "Old body", ["old"])
        async with Client(mcp) as client:
            result = await client.call_tool(
                "update_note", {"note_id": added, "content": "New body"}
            )
        return added, result

    added, result = _run(body)
    assert result.is_error is False
    assert result.structured_content["content"] == "New body"
    assert result.structured_content["title"] == "Old title"  # untouched field
