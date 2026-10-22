"""The MCP server surface: one ``MCPServer`` exposing our notes store.

Read this file top-to-bottom; it is written as a tutorial. The companion
document ``docs/02-building-the-server.md`` walks through it section by
section, and ``docs/01-what-is-mcp.md`` explains the protocol it speaks.

The mental model
----------------
    ┌────────────┐   JSON-RPC      ┌──────────────────┐    sqlite3   ┌─────────┐
    │  MCP host  │ ◄─────────────► │  this module     │ ───────────► │notes.db │
    │ (a client) │  over a stream  │  (MCPServer v2)  │              └─────────┘
    └────────────┘                 └──────────────────┘

We register *plain Python functions* on the ``MCPServer`` instance. The SDK
derives everything else — the JSON Schema the model sees, the descriptions,
the channel routing — from each function's name, signature, type hints and
docstring. That derivation is the reason we write so little code here.

Two class-level rules pin the whole design:

1. **stdout is protocol, not logging.** For a stdio transport the SDK reads
   JSON-RPC frames from our stdout; a single stray ``print()`` corrupts the
   stream and the client sees a protocol error. Notice there is no
   ``print`` anywhere in ``notes_mcp/`` — logging goes to stderr.
2. **Handlers are ordinary sync functions.** SDK v2 runs sync handlers on a
   worker thread, so blocking calls (here: ``sqlite3``) are safe; there is
   no need for an async driver.
"""

from __future__ import annotations

import logging
import sys
from logging import DEBUG, INFO, StreamHandler, getLogger
from typing import Annotated

from pydantic import BaseModel, Field

# The import paths worth memorising for MCP SDK v2 (they changed in v2 — the
# pre-2026 tutorials you will find online say `from mcp.server.fastmcp import
# FastMCP`, which is the legacy v1 spelling of exactly this class):
from mcp.server import MCPServer
from mcp.server.mcpserver.exceptions import ToolError, ResourceNotFoundError

from notes_mcp import db

# ---------------------------------------------------------------------------
# The server object — the thing a client actually connects to
# ---------------------------------------------------------------------------

# `instructions` is a server-provided tip that clients may put next to the
# tool descriptions when steering the model; `version` is what
# client.server_info.version will report after the handshake.
mcp = MCPServer(
    "notes",
    instructions="The notes server is the source of truth for the user's personal notes. "
    "Search or read BEFORE claiming anything about what notes exist.",
    version="1.0.0",
)

_LOG = getLogger("notes_mcp")
#: stderr-only verbosity: INFO when a host runs us, DEBUG when you run the
#: script yourself in a terminal. Never stdout — stdout is the protocol.
_LOG.setLevel(DEBUG if sys.stderr.isatty() else INFO)


# ---------------------------------------------------------------------------
# The data type half of structured output
# ---------------------------------------------------------------------------
# Any tool whose return type is a Pydantic model gets a *structured* result:
# the SDK publishes an output_schema (JSON Schema for this model) and the
# client receives `structured_content` (machine-readable JSON) in addition to
# the text blocks the model reads. Returning a model, not a string, is how we
# make `add_note` usable BOTH by an LLM (text) and by programmatic clients.

class Note(BaseModel):
    """One row of the notes table, as JSON. (Docstring lands in the schema.)"""

    id: int = Field(description="Permanent id in the database")
    title: str = Field(description="Short headline of the note")
    content: str = Field(description="Full text of the note")
    tags: list[str] = Field(default_factory=list, description="Free-form labels")
    created_at: str = Field(description="ISO-8601 UTC creation timestamp")
    updated_at: str = Field(description="ISO-8601 UTC last-modified timestamp")


def _note_from_row(row: dict) -> Note:
    """Convert a db-layer dict into the model (db stores tags as one string)."""
    return Note(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        tags=[t for t in row["tags"].split(",") if t],
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


def _format_note(note: Note) -> str:
    """Human/model-readable single-note rendering shared by several tools."""
    tags = f" [tags: {', '.join(note.tags)}]" if note.tags else ""
    return (
        f"Note #{note.id}: {note.title}{tags}\n"
        f"  Content: {note.content}\n"
        f"  Created: {note.created_at}  Updated: {note.updated_at}"
    )


# ---------------------------------------------------------------------------
# Tools — functions the MODEL decides to call
# ---------------------------------------------------------------------------
# typeof: docstring → the tool description the model reads to decide when to
# call; type hints → the input JSON Schema the model fills in. A parameter's
# Annotated[..., Field(description=...)] lets us document *parameters* just
# like the docstring documents the whole tool.

@mcp.tool()
def add_note(
    title: Annotated[str, Field(description="Short headline for the note")],
    content: Annotated[str, Field(description="Full text to store")],
    tags: Annotated[list[str] | None, Field(description="Optional labels")] = None,
) -> Note:
    """Create a note in the database and return it with its new id."""
    note_id = db.add_note(title, content, tags or [])
    return _note_from_row(db.get_note(note_id))  # type: ignore[arg-type]


@mcp.tool()
def search_notes(
    query: Annotated[str, Field(description="Words to look for; empty means 'list newest'")],
    limit: Annotated[int, Field(description="Max number of notes to return")] = 10,
) -> str:
    """Search the user's notes by title, content, or tag (case-insensitive).

    Returns a formatted text summary. This is the 'model-readable' tool
    style: a plain string comes back as text content with NO structured
    half, which is right for tools whose result is prose, not data.
    """
    notes = db.search_notes(query, limit)
    if not notes:
        return f"No notes match '{query}'."
    lines = [f"Found {len(notes)} note(s) matching '{query}':"]
    for row in notes:
        tags = [t for t in row["tags"].split(",") if t]
        tag_text = f" [{', '.join(tags)}]" if tags else ""
        lines.append(f"- #{row['id']} {row['title']}{tag_text}")
    return "\n".join(lines)


@mcp.tool()
def update_note(
    note_id: Annotated[int, Field(description="Id of the note to update")],
    title: Annotated[str | None, Field(description="New title; omit to keep")] = None,
    content: Annotated[str | None, Field(description="New text; omit to keep")] = None,
    tags: Annotated[list[str] | None, Field(description="Replaces all tags; omit to keep")] = None,
) -> Note:
    """Update one or more fields of an existing note.

    The failure contract matters: a missing id raises ToolError, which the
    SDK turns into `is_error=True` on the client with our message as the
    text content. The model then sees "Note 424242 not found" as ordinary
    tool output it can react to (try another id, tell the user, ...).
    Errors that are part of the conversation — not crashes.
    """
    updated = db.update_note(note_id, title=title, content=content, tags=tags)
    if updated is None:
        raise ToolError(f"Note {note_id} not found")
    return _note_from_row(updated)


@mcp.tool()
def delete_note(
    note_id: Annotated[int, Field(description="Id of the note to delete")],
) -> str:
    """Delete a note permanently and confirm."""
    if not db.delete_note(note_id):
        raise ToolError(f"Note {note_id} not found")
    return f"Deleted note {note_id}."


# ---------------------------------------------------------------------------
# Resources — data the APPLICATION decides to load into its model's context
# ---------------------------------------------------------------------------
# The same decorator family, a different controller: tools are chosen by the
# model mid-conversation; resources are attached by the host application (an
# IDE opening a file, or a UI showing a note). Resources are read-only data
# addressed by URI, and hey have NO `is_error` half-state: a read either
# returns contents or fails the whole request at the protocol level.
#
# `note://{id}` is a resource TEMPLATE: the `{id}` in the URI is bound to the
# function parameter, so "note://42" reads note 42 — but the URI being
# well-formed says nothing about the note existing. Only this function can
# answer that, with ResourceNotFoundError, which the SDK upgrades to the
# spec's -32602 (with the URI in `data`) — the shape clients raise as
# MCPError. That is deliberately different from a tool's ToolError: an
# application attaching a resource cannot "retry smarter" the way a model
# can, so there is no model-readable half-result to return.

@mcp.resource("note://{id}")
def read_note(id: int) -> str:
    """The full text of one note, addressed by id."""
    row = db.get_note(id)
    if row is None:
        raise ResourceNotFoundError(f"Note {id} not found")
    return _format_note(_note_from_row(row))


@mcp.resource("notes://stats")
def stats_text() -> str:
    """Live aggregate of the notes store: count and most recent update."""
    stats = db.stats()
    return (
        f"Total notes: {stats['count']}\n"
        f"Last updated: {stats['last_updated'] or 'never'}"
    )


# ---------------------------------------------------------------------------
# Entry point — what the console script (and therefore MCP hosts) runs
# ---------------------------------------------------------------------------

def main() -> None:
    """Console-script entry: prepare the database, then serve over stdio.

    * ``init_db`` is idempotent (safe every launch) and makes sure a fresh
      ``data/notes.db`` exists with its seed notes — our server owns its
      storage; nothing about it comes from the client.
    * ``run(transport="stdio")`` wires MCP's JSON-RPC framing to
      sys.stdin/sys.stdout and blocks until the client closes the stream
      (e.g. client.py exiting, or the host shutting down). EOF on stdin is
      the normal-ish shutdown signal.
    * stderr logging is safe (the one stream that is NOT protocol).
    """
    logging.root.addHandler(StreamHandler(sys.stderr))

    db.init_db()
    _LOG.info("notes MCP server starting (db: %s)", db.db_path())
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
