# 01 · What is MCP? (the mental model)

*Part of a guided tour — read in order: 01 → 02 → 03 → 04 → 05.*
*The code this document describes lives in `notes_mcp/` and `client.py`.*

---

## The problem MCP solves

Before MCP, every LLM application (Claude Desktop, an IDE agent, OpenCode) that
wanted to use *your* data or *your* tools had to learn about them one by one —
M applications × N integrations, every pair written by hand.

**MCP (Model Context Protocol)** collapses that to **M + N**: applications
implement the protocol once (they are *hosts*), and anyone can implement the
other side (a *server*) that speaks the same protocol. One notes server works
unchanged in every MCP host.

Think of it as **USB-C for tools**: the port is standardized; what you plug in
is up to you.

## The three roles

```
┌─────────────┐        ┌───────────────┐        ┌──────────────────┐
│     HOST    │ ─────► │ CLIENT (in    │ ◄────► │ SERVER (you      │
│ LLM app:    │ spawns │ host; speaks  │ JSON-  │ write with SDK   │
│ OpenCode,   │        │ MCP, one per  │ RPC    │ v2 in notes_mcp) │
│ Claude, IDE │        │ server)       │        │        │
└─────────────┘        └───────────────┘        └────────┼─────────┘
                                                          ▼
                                                   ┌─────────────┐
                                                   │ data/notes.db│
                                                   │ (the REAL    │
                                                   │  system)     │
                                                   └─────────────┘
```

- **Host** — the LLM application the user talks to. In this repo, `client.py`
  temporarily plays the host; in `docs/05` the host becomes OpenCode.
- **Client** — lives inside the host; maintains the MCP connection. One client
  per connected server. You never write it — the SDK's `Client` class is a
  reusable one (that's what `client.py` uses).
- **Server** — what this project is. It exposes capabilities; it **never talks
  to the model directly**. The host relays.

## What a server exposes: three primitives, three controllers

The key sentence from the SDK docs: what separates the primitives is **who
decides to use them**.

| Primitive | Controlled by | What it is | In this repo |
|---|---|---|---|
| **Tools** | The **model** | A function the model may call (with user approval) to act or fetch | `add_note`, `search_notes`, `update_note`, `delete_note` |
| **Resources** | The **application** | Read-only data the host loads into context (like a `GET`) | `note://{id}`, `notes://stats` |
| **Prompts** | The **user** | Reusable message templates invoked by name (like a slash command) | `summarize_notes(query)` |

Why the split matters: an *application* deciding to attach data (resource) can
happen without the model ever knowing; a *user* invoking a prompt must not
silently change state (prompts are message factories, they can't even call
tools); a *model* choosing to call a tool is the agentic loop — and the reason
hosts ask for approval before running a tool call.

## The wire: JSON-RPC over a transport

MCP messages are **JSON-RPC 2.0** frames. For this project's transport —
**stdio** — the host launches your server as a child process and writes
newline-delimited JSON-RPC to its stdin, reading frames from its stdout. That
is why two rules exist that you must internalize before writing any server:

1. **stdout is protocol, not logging.** One stray `print()` corrupts the
   stream. Log to stderr.
2. **The child does not inherit the parent's environment** (SDK v2 gives it a
   minimal allow-list). Anything the server needs must be passed explicitly
   (`env=` in `StdioServerParameters`, or baked into the package like our DB
   path).

The other standard transport is **Streamable HTTP** (`Client("http://.../mcp")`)
— what you deploy behind for remote servers. Same protocol verbs, different
plumbing. We stay on stdio because it is exactly what OpenCode and desktop
hosts run.

The protocol has **dated versions**. The SDK v2 we use implements the
**2026-07-28** spec — `client.protocol_version` in our demo prints exactly
that. You will find older tutorials (pre-2026) showing `FastMCP` imported from
`mcp.server.fastmcp`; v2 renamed that class to `MCPServer` (see `docs/02`).

## Capabilities: the handshake

On connect, the server declares what it can do:

```
prompts  → prompts/list, prompts/get
resources → resources/list, resources/templates/list, resources/read
tools     → tools/list, tools/call
```

The client only asks for declared capabilities. `MCPServer` declares these for
you automatically — because we registered at least one tool/resource/prompt.

## Why "connect to a real system" is the point

You asked for a server whose information is **not from the model's training
knowledge**. That is exactly what this project does, and it is worth stating
precisely why it works:

- The notes live in `data/notes.db` — rows on your disk. The model's weights
  contain nothing about them.
- Every `search_notes` / `read_resource` result is read from SQLite at call
  time. Delete the DB and the model has *nothing* to say about your notes.
- Even the prompt `summarize_notes` embeds database rows into the message, so
  the "summarize" it generates is grounded in stored text only.

That is the template for every real MCP server: *swap SQLite for your company
API, your calendar, your sensor — the architecture does not change.*

## Where to go next

- **02-building-the-server.md** — line-by-line tour of `db.py` + `server.py`.
- **03-talking-to-your-server.md** — how `client.py` speaks to it, and the
  three result fields (`content` / `structured_content` / `is_error`).
- **04-testing.md** — the in-memory `Client(mcp)` test pattern.
- **05-connecting-opencode.md** — register this server with a real host.

References:
- Python SDK v2 docs: <https://py.sdk.modelcontextprotocol.io/>
- Spec: <https://modelcontextprotocol.io/specification/latest>
- Migration (v1→v2, if you meet old tutorials):
  <https://py.sdk.modelcontextprotocol.io/migration/>
