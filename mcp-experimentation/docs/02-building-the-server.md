# 02 · Building the server (annotated walkthrough)

*Read after `docs/01-what-is-mcp.md`. This walks through the actual files,
quoting the shipped code.*

---

## File layout and why it is shaped like this

```
mcp-experimentation/
├── pyproject.toml        # packaging + the notes-server command + deps
├── notes_mcp/
│   ├── db.py             # SQLite layer — ZERO MCP imports
│   └── server.py         # MCPServer + tools/resources/prompt + main()
├── client.py             # the MCP client side (docs/03)
└── tests/                # in-memory client tests (docs/04)
```

The one-boundary-per-file rule mirrors what makes MCP servers maintainable:
`db.py` is "the real system", `server.py` is "the protocol façade". If
tomorrow the real system is a company REST API instead of SQLite, you rewrite
`db.py` and never touch the protocol code.

## `pyproject.toml` — what makes `notes-server` a real command

Three pieces do the work:

```toml
[project.scripts]
notes-server = "notes_mcp.server:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["notes_mcp"]
dev-mode-dirs = ["."]
```

- `[project.scripts]` — declares the console command `notes-server` that runs
  `notes_mcp.server.main()`. This is the exact string hosts will launch; a
  console script is what makes the server launchable **without the host
  knowing your directory layout**.
- `[build-system]` — turns the uv project into an installable package
  (`uv sync` installs it into `.venv`, editable by default).
- `dev-mode-dirs = ["."]` — **the lesson we hit the hard way**: a hatchling
  editable install otherwise contains *no import hook at all* (we proved this
  by unzipping the wheel: only `dist-info` + the script). The result was
  `ModuleNotFoundError: No module named 'notes_mcp'` whenever the server was
  launched from a different working directory — which is how every host
  launches servers. This line makes the editable wheel put the project root
  on `sys.path`, so imports work from any cwd. If you ship an MCP server as a
  package, this is the setting that keeps "works on my machine" from lying to
  you.

Dependencies: `mcp[cli]>=2.3.0` (SDK v2; the `[cli]` extra adds the `mcp dev`
inspector command). Nothing else — `sqlite3` and `pydantic` (transitive) cover
the rest.

## `notes_mcp/db.py` — the real system, in six ideas

**1. The path is anchored to the source file, not the cwd:**

```python
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "notes.db"

def db_path() -> Path:
    override = os.environ.get(DB_PATH_ENV)          # NOTES_DB_PATH
    return Path(override) if override else DEFAULT_DB_PATH
```

`__file__`-anchoring means: wherever a host's child process happens to start,
the same database file opens. The env override exists so the *tests* can swap
in an isolated file. Note `db_path()` reads the environment **at call time** —
reading it at import time would freeze the path before tests can set it.

**2. Schema + auto-seed (`init_db`)** — `CREATE TABLE IF NOT EXISTS notes ...`
plus two seed notes **only if the table is empty** (checked with `COUNT(*)`,
so calling `init_db()` every launch is safe and never duplicates).

**3. Connections are short-lived:** `connect()` opens a per-operation
connection with `row_factory = sqlite3.Row` (rows behave like dicts:
`row["title"]`). For a server that may be called repeatedly and
concurrently, per-call connections are the simplest correct pattern — SQLite
does its own file locking.

**4. Parameterized SQL, always:**

```python
pattern = f"%{query}%"
conn.execute("... WHERE title LIKE ? OR content LIKE ? OR tags LIKE ?", (pattern, pattern, pattern))
```

You are connecting an LLM's arguments to SQL — string-concatenating the query
into the SQL text would be textbook SQL injection. `?` placeholders make the
attack impossible and cost nothing.

**5. Search is `LIKE`-based and newest-first** (`ORDER BY updated_at DESC,
id DESC`). An empty query degenerates to `LIKE '%%'` → "list my newest notes".
That is documented behavior, pinned by a test (`test_search_empty_query_lists_recent`).

**6. Tags are one comma-joined string** — SQLite has no list type; splitting
happens once, in the server layer (`_note_from_row`). Normalizing tags into a
second table would be over-engineering for a teaching server (YAGNI).

### Why sync sqlite3 in an async server is fine

SDK v2 runs **sync handlers on a worker thread**, so a blocking `sqlite3`
call does not stall the event loop. Do not reach for an async DB driver out
of reflex; write the boring version first.

## `notes_mcp/server.py` — the protocol façade

### The server object

```python
from mcp.server import MCPServer        # v2 spelling! (v1: mcp.server.fastmcp.FastMCP)
from mcp.server.mcpserver.exceptions import ToolError, ResourceNotFoundError

mcp = MCPServer(
    "notes",
    instructions="The notes server is the source of truth for the user's personal notes. "
                 "Search or read BEFORE claiming anything about what notes exist.",
    version="1.0.0",
)
```

- The **name** is what clients display and what the handshake reports.
- **`instructions`** is a server-provided steering tip hosts may add to the
  model's context — we use it to prevent the classic failure of an LLM
  *inventing* notes instead of searching.
- Everything the model sees is **derived from your Python functions**: name →
  function name; description → docstring; input schema → type hints. You never
  write JSON Schema.

### Tools: `Annotated` fields + docstring = the model's view

```python
@mcp.tool()
def add_note(
    title: Annotated[str, Field(description="Short headline for the note")],
    content: Annotated[str, Field(description="Full text to store")],
    tags: Annotated[list[str] | None, Field(description="Optional labels")] = None,
) -> Note:
    """Create a note in the database and return it with its new id."""
    note_id = db.add_note(title, content, tags or [])
    return _note_from_row(db.get_note(note_id))
```

- `@mcp.tool()` turns the function into a tool; the docstring becomes the
  description the model reads when deciding *whether* to call it — write it
  for the model, not for yourself.
- `Annotated[..., Field(description=...)]` documents *parameters* the same way.
- SDK rejects arguments that violate the schema **before** your function runs —
  so never re-validate your own hints inside the handler.

### Structured output: return a Pydantic model

```python
class Note(BaseModel):
    id: int
    title: str
    content: str
    tags: list[str]
    created_at: str
    updated_at: str
```

Returning `Note` (not `str`) makes the SDK publish an `output_schema` for the
tool, and clients receive the return value as **`structured_content`** (JSON)
*in addition to* the text blocks the model reads. One return, two consumers:
`content` for the model, `structured_content` for programmatic code. That is
what makes `add_note` equally good for an LLM and a script.

### The error contract: `ToolError` is a message TO the model

```python
if not db.delete_note(note_id):
    raise ToolError(f"Note {note_id} not found")
```

A missing id is a *normal, expected* outcome of a model guessing ids — so it
must be information the model can act on. `ToolError` does exactly that: the
client-side call **returns normally** with `is_error=True` and the message in
`content` ("Error executing tool delete_note: Note 999 not found" — you can
see this in the demo's step 7 output). Nothing is raised at the caller.

Contrast with `MCPError` (protocol failure: the *host* gets a JSON-RPC error,
the model sees nothing) — reserved for conditions no smarter model could fix.
Rule of thumb from the SDK docs: **"Could a smarter model have avoided this?"
Yes → `ToolError`. No → `MCPError`.**

And never `return` an error string instead of raising: a returned string has
`is_error=False`, so it *looks* like success to every client.

### Resources: templates vs concrete, and `ResourceNotFoundError`

```python
@mcp.resource("note://{id}")          # TEMPLATE — {id} binds to the parameter
def read_note(id: int) -> str:
    row = db.get_note(id)
    if row is None:
        raise ResourceNotFoundError(f"Note {id} not found")
    return _format_note(_note_from_row(row))

@mcp.resource("notes://stats")        # CONCRETE — fixed URI
def stats_text() -> str: ...
```

The two land in **different listings** (`resources/list` vs
`resources/templates/list`) because a template isn't readable until filled in.
Resources have no `is_error` half-state: a read returns contents or fails the
request as a **protocol** error — `ResourceNotFoundError` becomes `-32602`
with the URI in `data`, and clients see that as a raised `MCPError`
(`docs/03` shows both error shapes side by side).

### The prompt: a message factory that may read the store

```python
@mcp.prompt()
def summarize_notes(query: str) -> str:
    rows = db.search_notes(query, limit=5)
    ...
    return f"Summarize ... ONLY on the notes below:\n\n" + bullets
```

The returned string becomes a **user message**. Because it is a plain
function it can hit `db` directly — embedding real rows so the summary is
grounded in the database, not training data.

### `main()` — the entry the console script runs

```python
def main() -> None:
    logging.root.addHandler(StreamHandler(sys.stderr))  # stderr only
    db.init_db()                       # idempotent; owns our storage
    mcp.run(transport="stdio")         # JSON-RPC on stdin/stdout, blocks until EOF
```

`run(transport="stdio")` blocks; the client closing stdin (demo exit, host
shutdown) is the shutdown signal. During `main()`'s whole life, stdout
carries nothing but protocol.

## What you did NOT write

A JSON Schema. Request routing. Capability negotiation. Version handshaking.
Transport framing. All of that is the SDK. The code you *do* write is: the
data layer, and one decorated function per capability. That ratio —
"decorated functions over a real system" — is the recommended way.

## Next

`docs/03-talking-to-your-server.md` — the other half: how `client.py` launches
this thing and what comes back over the wire.
