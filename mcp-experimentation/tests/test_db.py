"""Unit tests for ``notes_mcp.db`` — the pure-SQLite data layer.

These tests deliberately know nothing about MCP: the database layer is an
ordinary Python module, and testing it requires no protocol, client, or
subprocess (that is what tests/test_server.py is for).

Every test pins the ``NOTES_DB_PATH`` environment variable to a fresh file
in pytest's ``tmp_path`` so it can never touch the real ``data/notes.db``
that the demo client reads and writes.
"""

from notes_mcp import db


def _fresh(tmp_path, monkeypatch):
    """Point the DB at a per-test file and initialise it."""
    monkeypatch.setenv("NOTES_DB_PATH", str(tmp_path / "test.db"))
    db.init_db()


def test_db_path_is_cwd_independent(tmp_path, monkeypatch):
    """The default DB location is derived from the package file, not cwd.

    A host (client.py today, OpenCode later) may launch the server process
    from any working directory — if the path were cwd-relative the server
    would silently create a brand-new database somewhere else.
    """
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("NOTES_DB_PATH", raising=False)
    assert db.db_path() == db.DEFAULT_DB_PATH


def test_add_get_roundtrip(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    note_id = db.add_note("Quarter plan", "Learn MCP basics", ["study", "mcp"])
    row = db.get_note(note_id)
    assert row is not None
    assert row["id"] == note_id
    assert row["title"] == "Quarter plan"
    assert row["content"] == "Learn MCP basics"
    assert row["tags"] == "study,mcp"
    assert "T" in row["created_at"]  # ISO-8601 UTC string


def test_seed_on_first_init(tmp_path, monkeypatch):
    """An empty database auto-seeds two demo notes so the server is not blank."""
    _fresh(tmp_path, monkeypatch)
    assert db.stats()["count"] == 2


def test_seed_does_not_duplicate(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    db.init_db()  # second call must not insert the seeds again
    assert db.stats()["count"] == 2


def test_search_finds_case_insensitively_and_orders_newest_first(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    newest = db.add_note("Jellyfish migration", "Annual bloom near the nets.", ["biology"])
    hits = db.search_notes("jellyfish")  # lowercase query vs Title Case row
    assert [h["id"] for h in hits] == [newest]


def test_search_empty_lists_recent(tmp_path, monkeypatch):
    """An empty query matches everything (LIKE '%%') — newest first, not an error."""
    _fresh(tmp_path, monkeypatch)
    added = db.add_note("Fresh note", "", [])
    hits = db.search_notes("")
    assert hits[0]["id"] == added
    assert len(hits) >= 2


def test_search_limit(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    hits = db.search_notes("", limit=1)
    assert len(hits) == 1


def test_update_partial_fields(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    note_id = db.add_note("Title A", "Body untouched", ["t1"])
    updated = db.update_note(note_id, title="Title B")
    assert updated["title"] == "Title B"
    assert updated["content"] == "Body untouched"
    assert updated["updated_at"] >= updated["created_at"]


def test_update_tags_replaces_list(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    note_id = db.add_note("T", "C", ["old"])
    updated = db.update_note(note_id, tags=["new1", "new2"])
    assert updated["tags"] == "new1,new2"


def test_update_missing_returns_none(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    assert db.update_note(424242, title="x") is None


def test_delete_roundtrip(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    note_id = db.add_note("Doomed", "Bye", [])
    assert db.delete_note(note_id) is True
    assert db.get_note(note_id) is None


def test_delete_missing_returns_false(tmp_path, monkeypatch):
    _fresh(tmp_path, monkeypatch)
    assert db.delete_note(424242) is False
