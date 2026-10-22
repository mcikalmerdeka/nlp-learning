# 03 · Talking to your server (the client side)

*Read after `docs/02-building-the-server.md`. This walks through
`client.py`, the miniature host.*

---

## The one class: `Client`

```python
from mcp import Client, StdioServerParameters
```

A `Client` is how a Python program speaks MCP. Its transport is chosen from
the single argument you pass:

| You pass | It does |
|---|---|
| a URL string (`"http://localhost:8000/mcp"`) | Streamable HTTP (the deployed-server transport) |
| a `StdioServerParameters` | **launches the server as a child process**, speaks JSON-RPC over its stdin/stdout — what hosts do |
| the server object (`Client(mcp)`) | in-process (tests only — `docs/04`) |

## How our demo launches the server

```python
SERVER = StdioServerParameters(
    command="uv",
    args=["run", "--directory", str(PROJECT_ROOT), "notes-server"],
)

async with Client(SERVER) as client:
    ...                       # the whole conversation lives in this block
# leaving the block shut the child down — we never manage the process
```

Three subprocess facts worth internalizing (they are the difference between
"works on my machine" and works):

1. **Entering the block spawns the process; leaving it shuts it down**
   (close stdin → wait → kill if it lingers). There is no `connect()`/
   `close()` pair in v2; the context manager IS the lifecycle.
2. **The child gets a minimal environment** (HOME/LOGNAME/PATH/SHELL/TERM/USER
   on POSIX — nothing else). Secrets/settings must go through
   `StdioServerParameters(env={...})` explicitly. Our server needs none — its
   DB path is a property of the package (`docs/02`).
3. **The child's stderr surfaces in yours** (that is why the demo prints the
   server's log lines before step 1). Its stdout is protocol — never yours to
   read.

## Step by step through the demo

`uv run client.py` prints nine banner steps. Each maps to one client verb:

| Step | Verb | What you learn |
|---|---|---|
| 1 | connect | `server_info`, `server_capabilities`, `protocol_version` (`2026-07-28`), `instructions` are **already populated** at block entry |
| 2 | `list_tools()` | the exact definitions a host hands its model (name, description, `input_schema`) |
| 3 | `list_resources()` + `list_resource_templates()` | concrete vs templated URIs — two different lists |
| 4 | `call_tool("add_note", {...})` | **structured output**: one result, two consumers |
| 5 | `read_resource("note://{id}")` | data by URI — no schema needed, it IS the URI |
| 6 | `call_tool("search_notes", {...})` | plain-string tool → text content only |
| 7 | `call_tool("delete_note", {"note_id": 999})` | the error contract (below) |
| 8 | `get_prompt("summarize_notes", {"query": "mcp"})` | prompts render to **messages** the host sends to a model |
| 9 | `read_resource("notes://stats")` | server-side aggregates, read like any resource |

## The anatomy of a tool result

```python
added = await client.call_tool("add_note", {"title": ..., "content": ..., "tags": ["demo"]})

added.is_error            # False — check this FIRST, always
added.content             # [TextContent(...)] — what the MODEL reads (always text-shaped)
added.structured_content  # {'id': 3, 'title': ..., 'tags': [...]} — what YOUR CODE reads
```

- **`content`** is a *list* of typed blocks (`TextContent`, `ImageContent`,
  `AudioContent`, `ResourceLink`, `EmbeddedResource`) — narrow with
  `isinstance(block, TextContent)` before touching `.text`; a `ImageContent`
  has `.data`, not `.text`.
- **`structured_content`** exists only when the tool's return type declares a
  schema (our Pydantic `Note`). `None` for string-returning tools like
  `search_notes`.
- Both halves carry the same data *on purpose*: text for a model, JSON for code.

## The three error shapes (this is the exam question)

**1. Expected tool failure → `is_error=True`, no exception raised:**

```python
result = await client.call_tool("delete_note", {"note_id": 999})
result.is_error   # True
result.content    # [TextContent(text="Error executing tool delete_note: Note 999 not found")]
result.structured_content  # None
```

The server raised `ToolError` (`docs/02`); the SDK turned it into an ordinary
result the model can read and react to. A tool error is a turn in the
conversation, not a crash. An unexpected crash in a handler looks similar but
hides the internals: `content` says only `Error executing tool <name>` — the
traceback goes to the *server's* stderr log, deliberately.

**2. Protocol failure → the client RAISES `MCPError`:**

```python
await client.read_resource("note://424242")
# raises: MCPError(-32602, 'Note 424242 not found', {'uri': 'note://424242'})
```

Missing resources (and unknown tools/methods) fail the *whole request* with a
JSON-RPC error — the host application's problem to handle, not something a
model could retry smarter. `code`, `message`, `data` arrive intact.

**3. Bad arguments never reach *your handler*** — the **server** validates the
arguments against the tool's input schema before the function runs, and
answers with an `is_error=True` result carrying the pydantic validation
message. Your handler code never executes for a malformed call, so you never
write that validation yourself (the SDK logs it server-side:
`Tool 'add_note' rejected arguments: ['title']`).

So: **always check `is_error` before trusting a result**, and treat a raised
`MCPError` as "the request itself was invalid" rather than "the tool failed".

## The result is honest about media types

`read_resource` returns `contents`: a list of `TextResourceContents` or
`BlobResourceContents` — narrow before reading `.text`/`.blob`, same discipline
as tool content blocks.

## From here: a real host

`docs/05-connecting-opencode.md` registers this same stdio command
(`uv --directory <project> run notes-server`) in OpenCode. Nothing about the
server changes — the host simply replaces `client.py` as the thing on the
other side of the pipe, plus an LLM in the loop deciding which tools to call.
