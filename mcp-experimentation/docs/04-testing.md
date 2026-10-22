# 04 · Testing an MCP server (the in-memory client pattern)

*Read after `docs/03-talking-to-your-server.md`.*

---

## The pattern, and why it is the recommended one

The SDK v2 ships a `Client` that connects **in-process**: hand it the server
*object* instead of a URL or subprocess parameters and every verb works over
the real protocol layer — validation, capability negotiation, JSON-RPC
dispatch — with no process, no port, and no flaky stdio plumbing:

```python
from mcp import Client
from notes_mcp.server import mcp          # the MCPServer instance

async with Client(mcp) as client:
    result = await client.call_tool("add_note", {"title": "T", "content": "C"})
    assert result.structured_content["title"] == "T"
```

This is not a shortcut we invented — it is how the SDK's own documentation
tests every example on its pages (their CI runs these snippets through an
in-memory client, so the docs cannot silently rot). For your own servers it
gives you: deterministic tests, no ports to leak, no subprocess timeouts, and
full protocol semantics (the interesting parts — schema validation, error
shaping — all still happen).

## The two test files

```
tests/
├── test_db.py       # pure SQLite layer: no MCP, no protocol
├── test_server.py   # the MCP surface, via in-memory Client(mcp)
```

The split follows the architecture: `db.py` has no MCP concepts in it, so its
tests need none. `test_server.py` pins what a *host* experiences. Because the
in-process client and the handlers share one Python process, the database
tests and protocol tests would collide on `data/notes.db` without isolation —

## Isolation: the `NOTES_DB_PATH` fixture

```python
@pytest.fixture
def fresh_db(tmp_path, monkeypatch):
    monkeypatch.setenv("NOTES_DB_PATH", str(tmp_path / "server-test.db"))
    db.init_db()
```

`db.db_path()` reads the environment **at call time** (`docs/02` explains why
that matters), so a fixture-only `setenv` repoints every handler call during
one test — the real `data/notes.db` is never touched by tests, and every test
starts from a freshly seeded two-note store.

## The run shim

```python
def _run(coro_fn):
    return anyio.run(coro_fn)     # anyio ships with the SDK — no extra plugin
```

Each test's `body()` opens its own `async with Client(mcp)` block — that
context manager is the connection lifecycle — and the shim drives it from
synchronous pytest. No `pytest-asyncio` needed.

## What each test pins (and the failures worth studying)

**test_db.py** — path resolution, CRUD round trips, seeding/dedup, search
ordering, partial updates. The unusual one:

```python
def test_db_path_is_cwd_independent(...):
    monkeypatch.chdir(tmp_path)                    # pretend a host launched us elsewhere
    assert db.db_path() == db.DEFAULT_DB_PATH      # must not follow the cwd
```

That is the test for the exact bug class hosts expose: a cwd-relative DB path
would silently create a fresh database wherever the launcher happened to run.

**test_server.py** — surface and contracts:

- `test_list_tools_names` — the exact tool set a host's model gets offered.
- `test_add_note_structured_output` — Pydantic return ⇒ `structured_content`
  populated (and the text half mirrors it).
- `test_search_empty_query_lists_recent` — empty query is "list newest",
  not an error.
- `test_delete_missing_note_is_error` / `test_update_missing_note_is_error` —
  `ToolError` ⇒ `is_error=True` with the model-readable message
  ("Error executing tool delete_note: Note 999 not found"). Assert the flag
  and the *text*, because that text is what the model sees.
- `test_read_missing_note_resource_raises_protocol_error` — the DIFFERENT
  shape: resource reads fail the whole request; the client raises `MCPError`
  (`-32602`, URI in `data`).
- `test_stats_resource`, `test_list_resources_vs_templates`, prompt tests —
  capability listing and template rendering.

## The anyio `ExceptionGroup` subtlety (you will meet it in your own tests)

anyio runs handlers inside TaskGroups; a raised error is re-raised wrapped in
a (single-member) `ExceptionGroup`. A plain `pytest.raises(MCPError)` can
miss it. The repo's helper unwraps before asserting:

```python
def _unwrap(exc):
    while isinstance(exc, BaseExceptionGroup) and len(exc.exceptions) == 1:
        exc = exc.exceptions[0]
    return exc

with pytest.raises(BaseException) as info:
    _run(body)
error = _unwrap(info.value)
assert isinstance(error, MCPError)
```

Real transports unwrap this before hosts see it — the test reflects the
observable protocol error, not the concurrency artifact.

## Running

```bash
uv run pytest              # everything
uv run pytest tests/test_server.py -v          # the protocol surface
uv run client.py           # the live stdio walkthrough (docs/03)
```

Two runs of `client.py` are themselves a persistence test: the second run must
see the first run's note (ids keep incrementing; `notes://stats` keeps growing).

## What we deliberately do NOT test over stdio

`client.py` itself is verified by running it (`docs/03`), not unit-tested:
it exists to teach the stdio dance, and the in-memory tests already pin every
server behavior it exercises. The one stdio-specific behavior a host config
could break — launching `notes-server` from a foreign cwd — is pinned twice:
by `test_db_path_is_cwd_independent` and by `dev-mode-dirs` in packaging
(`docs/02`).
