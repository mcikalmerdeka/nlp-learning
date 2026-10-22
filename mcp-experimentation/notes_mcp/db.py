"""The SQLite data layer — "the real system" our MCP server connects to.

Why this file exists as its own module
--------------------------------------
An MCP server is interesting to a model only because of what sits *behind*
it: files, databases, APIs, devices. Everything that knows about SQLite
lives here, and nothing in here knows about MCP. The server module imports
these functions and exposes them over the Model Context Protocol; if one
day you swap SQLite for a company REST API, you only rewrite this file.

Two rules that make this layer safe to be launched by *any* MCP client:

1. **The database path is never cwd-relative.** An MCP client launches the
   server as a child process from *its own* working directory (you will
   see this in ``client.py``). If the path were ``"data/notes.db"`` relative
   to ``os.getcwd()``, each launcher would end up with a different
   database. Anchoring the default to ``Path(__file__)`` — the location of
   *this source file* — makes the location a property of the project,
   not of whoever launched it. ``NOTES_DB_PATH`` provides an explicit
   override (used heavily by the tests to get an isolated database).
2. **No printing.** A stdio MCP server's stdout *is* its JSON-RPC channel;
   any stray ``print()`` here would corrupt the protocol stream (this is
   the #1 mistake in hand-rolled MCP servers — see ``docs/02``).
   The same discipline applies to this layer even though it is MCP-blind.

Everything here is synchronous ``sqlite3`` code — perfectly fine for MCP:
SDK v2 runs sync handlers on a worker thread, so blocking on SQLite does
not stall the event loop (see ``docs/02-building-the-server.md``).

Storage design in one glance::

    notes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT, content TEXT,
        tags TEXT,             -- comma-joined, e.g. "study,mcp"
        created_at TEXT, updated_at TEXT   -- ISO-8601 UTC strings
    )

Tags are stored as a plain string because SQLite has no list type; SQL
search across them with a simple ``LIKE``. (Normalising into a second
table would be over-engineering for a teaching server — YAGNI.)
"""

from __future__ import annotations

import os
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Where the database lives
# ---------------------------------------------------------------------------

DB_PATH_ENV = "NOTES_DB_PATH"

#: ``__file__`` is ``<project>/notes_mcp/db.py`` → the parent is ``<project>``.
#: Going two levels up pins the default to the *project directory*, which is
#: stable no matter what cwd the launching process had.
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "notes.db"


def db_path() -> Path:
    """Resolve the database file path at *call* time, never at import time.

    Reading the environment inside the function (rather than at module
    import) is what lets the tests swap in an isolated database via
    ``monkeypatch.setenv`` *after* this module is already imported.
    """
    override = os.environ.get(DB_PATH_ENV)
    return Path(override) if override else DEFAULT_DB_PATH


def connect() -> sqlite3.Connection:
    """Open a per-call connection.

    A short-lived connection per operation is the safest pattern for a
    server that may be called concurrently: SQLite handles file locking,
    and each call starts and ends a well-defined transaction. The ``row_factory``
    makes rows behave like read-only dicts, so handlers can use ``row["title"]``.
    """
    connection = sqlite3.connect(str(db_path()), timeout=5.0)
    connection.row_factory = sqlite3.Row
    return connection


def _now() -> str:
    """ISO-8601 UTC timestamp as a sortable string (datetime.now() of the epoch)."""
    return datetime.now(timezone.utc).isoformat()


# ---------------------------------------------------------------------------
# Schema + seeding
# ---------------------------------------------------------------------------

_SCHEMA = """
CREATE TABLE IF NOT EXISTS notes (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    title      TEXT NOT NULL,
    content    TEXT NOT NULL,
    tags       TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
"""

#: Two starter notes so a brand-new ``data/notes.db`` is immediately useful —
#: the demo client can search/(re)discover something real on first contact.
_SEED_NOTES: list[tuple[str, str, str]] = [
    (
        "Welcome to the notes MCP server",
        "This note lives in a real SQLite file on your disk — data/notes.db. "
        "Whatever an LLM tells you about this note came from this database, "
        "not from its training data. Try searching, editing, or deleting it "
        "with the tools this server exposes.",
        "meta,getting-started",
    ),
    (
        "How MCP connects agents to real tools",
        "An MCP server exposes three primitives: tools (model-controlled "
        "actions), resources (application-controlled data), and prompts "
        "(user-controlled templates). This notes server demonstrates all "
        "three against one SQLite file.",
        "mcp,concepts",
    ),
]


def init_db() -> None:
    """Create the schema if needed, then seed if the table is empty.

    Called once at the bottom of ``server.py``'s ``main()`` — and by every
    test — but safe to call repeatedly (``CREATE TABLE IF NOT EXISTS``,
    and the seed check looks at ``COUNT(*)`` so re-initialising never
    duplicates data).
    """
    db_path().parent.mkdir(parents=True, exist_ok=True)
    with connect() as conn:
        conn.executescript(_SCHEMA)
        count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        if count == 0:
            timestamp = _now()
            conn.executemany(
                "INSERT INTO notes (title, content, tags, created_at, updated_at) "
                "VALUES (?, ?, ?, ?, ?)",
                [
                    (title, content, tags, timestamp, timestamp)
                    for title, content, tags in _SEED_NOTES
                ],
            )


# ---------------------------------------------------------------------------
# Row helpers (sqlite3.Row → plain dict for the server layer)
# ---------------------------------------------------------------------------

def _row_to_dict(row: sqlite3.Row) -> dict:
    return {
        "id": row["id"],
        "title": row["title"],
        "content": row["content"],
        "tags": row["tags"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


# ---------------------------------------------------------------------------
# CRUD operations — the functions the MCP server will expose
# ---------------------------------------------------------------------------

def add_note(title: str, content: str, tags: list[str]) -> int:
    """Insert a note and return its new id."""
    timestamp = _now()
    with connect() as conn:
        cursor = conn.execute(
            "INSERT INTO notes (title, content, tags, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (title, content, ",".join(tags), timestamp, timestamp),
        )
        return int(cursor.lastrowid)


def get_note(note_id: int) -> dict | None:
    """Fetch one note by id, or ``None`` if it does not exist."""
    with connect() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        return _row_to_dict(row) if row is not None else None


def search_notes(query: str, limit: int = 10) -> list[dict]:
    """Case-insensitive substring search over title/content/tags.

    ``LIKE`` in SQLite is case-insensitive for ASCII by default, so
    ``"jellyfish"`` matches a note titled "Jellyfish migration". An empty
    query degenerates to ``LIKE '%%'`` — i.e. "list my newest notes", which
    is documented behaviour rather than an error (pinned by a test).

    ``?`` placeholders are used for *every* interpolated value — string
    concatenation of user input into SQL would be a classic injection bug
    and a terrible thing to teach in a file about "connecting an LLM to
    tools".
    """
    pattern = f"%{query}%"
    with connect() as conn:
        rows = conn.execute(
            "SELECT * FROM notes "
            "WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? "
            "ORDER BY updated_at DESC, id DESC "
            "LIMIT ?",
            (pattern, pattern, pattern, limit),
        ).fetchall()
        return [_row_to_dict(row) for row in rows]


def update_note(
    note_id: int,
    title: str | None = None,
    content: str | None = None,
    tags: list[str] | None = None,
) -> dict | None:
    """Update only the fields that were provided (partial update).

    ``None`` means "leave this column alone" — the tool layer maps its
    optional parameters straight onto this. Returns the refreshed note,
    or ``None`` when the id does not exist (the server turns that into a
    ``ToolError`` the model can react to).
    """
    updates: list[str] = []
    params: list[object] = []
    if title is not None:
        updates.append("title = ?")
        params.append(title)
    if content is not None:
        updates.append("content = ?")
        params.append(content)
    if tags is not None:
        updates.append("tags = ?")
        params.append(",".join(tags))
    with connect() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id = ?", (note_id,)).fetchone()
        if row is None:
            return None
        if updates:  # even a no-field update refreshes updated_at, so the
            updates.append("updated_at = ?")  # "newest first" ordering stays honest
            params.append(_now())
            conn.execute(
                f"UPDATE notes SET {', '.join(updates)} WHERE id = ?",
                (*params, note_id),
            )
        refreshed = conn.execute(
            "SELECT * FROM notes WHERE id = ?", (note_id,)
        ).fetchone()
        return _row_to_dict(refreshed)


def delete_note(note_id: int) -> bool:
    """Delete a note by id; ``True`` if something was actually deleted."""
    with connect() as conn:
        cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        return cursor.rowcount > 0


def stats() -> dict:
    """Cheap aggregate used by the ``notes://stats`` resource."""
    with connect() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS count, MAX(updated_at) AS last_updated FROM notes"
        ).fetchone()
        return {"count": row["count"], "last_updated": row["last_updated"]}
