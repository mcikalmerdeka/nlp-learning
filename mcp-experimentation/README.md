# mcp-experimentation

A hands-on scaffold for learning the **Model Context Protocol (MCP)** by
building and consuming a real server — the recommended way, as of the
official Python SDK **v2** (protocol spec `2026-07-28`).

What you build: a **notes server** whose data lives in a real SQLite file.
An agent connected through MCP can *never* answer questions about these notes
from training knowledge — every read comes from disk. That is the point of
MCP: a standard connector between an LLM host and a system it has no internal
knowledge of.

## The tour (read in order)

| # | File | What it teaches |
|---|---|---|
| 1 | [`docs/01-what-is-mcp.md`](docs/01-what-is-mcp.md) | The mental model: host/client/server, tools vs resources vs prompts, JSON-RPC over stdio, capabilities |
| 2 | [`docs/02-building-the-server.md`](docs/02-building-the-server.md) | Annotated tour of `pyproject.toml`, `notes_mcp/db.py`, `notes_mcp/server.py` |
| 3 | [`docs/03-talking-to-your-server.md`](docs/03-talking-to-your-server.md) | The client side (`client.py`): lifecycle, verbs, result anatomy, the three error shapes |
| 4 | [`docs/04-testing.md`](docs/04-testing.md) | The SDK's recommended in-memory `Client(mcp)` test pattern |
| 5 | [`docs/05-connecting-opencode.md`](docs/05-connecting-opencode.md) | Register this server with OpenCode — a real host with a real LLM |

Design & process artifacts: `docs/superpowers/specs/…-design.md` and
`docs/superpowers/plans/…-notes-mcp-server.md`.

## Quickstart

```bash
uv sync                       # install deps + this package (editable)
uv run pytest                 # 26 tests over the real protocol layer (in-memory)
uv run client.py              # scripted walkthrough: launches the server as a
                              # subprocess and exercises every verb over stdio
```

Run `client.py` twice — the second run must still see the first run's notes
(ids keep incrementing). That is the "real system" doing its job.

## The project, at a glance

```
notes_mcp/
├── db.py        # the real system: SQLite CRUD, cwd-independent path, auto-seed
└── server.py    # the MCP façade: MCPServer v2 + 4 tools + 2 resources + 1 prompt
client.py        # a miniature MCP host (stdio subprocess + JSON-RPC)
data/notes.db    # created & seeded on first launch (gitignored)
tests/           # in-memory protocol tests (pytest)
```

Server surface:

- **Tools** (model-controlled): `add_note`, `search_notes`, `update_note`, `delete_note`
- **Resources** (application-controlled): `note://{id}` template, `notes://stats`
- **Prompt** (user-controlled): `summarize_notes(query)`

## Things worth stealing for your own server

- **stdout is protocol** — never `print()` in a stdio server; log to stderr.
- **Package it** — the `[project.scripts]` `notes-server` entry point is what
  hosts launch; `dev-mode-dirs = ["."]` keeps editable installs importable
  from any cwd (we hit that failure for real — see `docs/02`).
- **`ToolError` for model-fixable failures, `MCPError` for protocol failures.**
- **Anchor file paths to `__file__`**, never to the cwd — hosts launch servers
  from *their* working directory.
- **Test with `Client(mcp)`** — real protocol semantics, zero plumbing.
