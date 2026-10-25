# 05 · Connecting OpenCode (your first real host)

*Read last. Until now, `client.py` played the host. Here OpenCode takes over —
the same stdio command, but with a real LLM deciding which tools to call.*

---

## What actually changes

Nothing about the server. OpenCode:

1. reads its **config**,
2. launches `notes-server` as a **child process** (exactly like
   `StdioServerParameters` did),
3. negotiates the protocol,
4. and then the **model** — not your script — picks the tools from
   `tools/list` and calls them, with you approving in the UI.

That last step is the agentic loop, and it is the payoff of everything in
`docs/01`.

## Step 1 — register the server

**Option A: the CLI (recommended — it preserves unrelated config):**

```sh
opencode mcp add notes -- uv --directory "E:/NLP Learning/mcp-experimentation" run notes-server
```

(Forward slashes work in Windows paths everywhere, including JSON. If you
prefer backslashes, escape them: `E:\\NLP Learning\\...`.)

**Option B: by hand**, in project config (`opencode.jsonc` in this project)
or global (`~/.config/opencode/opencode.jsonc` — V2 field names, snake_case):

```jsonc
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "notes": {
        "type": "local",
        "command": ["uv", "--directory", "E:/NLP Learning/mcp-experimentation", "run", "notes-server"],
        "environment": {
          "NOTES_DB_PATH": "{env:NOTES_DB_PATH}"
        }
      }
    }
  }
}
```

Notes on the fields (from the OpenCode V2 MCP docs):

- `type: "local"` — a stdio server OpenCode starts itself. (A `remote` server
  would be Streamable HTTP + a URL — same protocol, different plumbing.)
- `command` — executable + arguments, one JSON array. `uv --directory ...`
  makes the launch independent of where OpenCode happens to run.
- `environment` — *added* to OpenCode's inherited env. `{env:NAME}` performs
  substitution; never paste secrets into config. Ours is optional: delete the
  block unless you want to repoint the database.
- A `cwd` field also exists (defaults to the workspace) — using
  `uv --directory` above makes the launch not care about it.

## Step 2 — verify the connection

```sh
opencode mcp list
```

Expect:

```text
✓ notes  connected
```

In the TUI, `/mcps` shows the same servers with connect/disconnect controls.

## Step 3 — what the model now sees

With the server connected, OpenCode adds to its system prompt the server's
`instructions` (ours: "search or read BEFORE claiming anything about what
notes exist") and exposes the tools. Naming follows the docs: tools are
`<server>_<tool>`, normalized:

| MCP name | OpenCode name |
|---|---|
| `add_note` | `notes_add_note` |
| `search_notes` | `notes_search_notes` |
| `update_note` | `notes_update_note` |
| `delete_note` | `notes_delete_note` |
| resource `note://{id}` | via built-ins `list_mcp_resources` / `read_mcp_resources` |
| prompt `summarize_notes` | command `/notes:summarize_notes <query>` |

(Under the default **Code Mode**, tools are grouped by server name instead:
`tools.notes.add_note(...)` — same capability, different call surface.)

## Step 4 — try it for real

Ask OpenCode something the model *cannot know*:

> List my notes about MCP.

Watch: the model calls `notes_search_notes`, OpenCode asks your approval, the
tool reads `data/notes.db`, and the answer quotes rows from disk. Then try
`"add a note that my demo passed"`, re-ask, and confirm the new note shows up
— persistence across processes, with no training-data involvement.

The deliberate-failure case also transfers: `"delete note 999"` should come
back as an `is_error` tool result the model *reads* ("Note 999 not found") and
reacts to — try another id or tell you — exactly the self-correcting loop
`docs/02` designed for.

## Protocol version (why you don't need to set it)

OpenCode opens every server with the classic `initialize` handshake
(`protocol: "legacy"`, the default) — and the MCP SDK v2 servers serve **both
protocol eras from one server with no configuration**, so our server answers
the legacy handshake fine. If you want OpenCode to *prefer* the modern
`2026-07-28` sessionless connection (probe then fall back), set one field:

```jsonc
"notes": { "type": "local", "command": [...], "protocol": "auto" }
```

## Permissions (optional but idiomatic)

Deny/allow per tool by the normalized name without disconnecting:

```jsonc
{
  "permissions": [
    { "action": "notes_delete_note", "resource": "*", "effect": "deny" },
    { "action": "notes_*",           "resource": "*", "effect": "allow" }
  ]
}
```

## Troubleshooting

| Symptom | Likely cause / fix |
|---|---|
| `mcp list` shows failed/never connects | `uv` not on PATH for OpenCode → use the absolute path (`where.exe uv`), or check the log: `~/.local/share/opencode/log/opencode.log` (filter `role=server`) |
| Server starts then dies | Launch it yourself to see stderr: `uv --directory "E:/NLP Learning/mcp-experimentation" run notes-server` (it exits on stdin EOF — that is normal for a piped start) |
| `No module named 'notes_mcp'` | The packaging lesson from `docs/02`: `dev-mode-dirs` missing, or the package was never `uv sync`-ed in this environment |
| Notes seem to "reset" | A cwd-relative DB path got repointed — our default anchors to the project; check you did not set `NOTES_DB_PATH` somewhere else |
| JSON config errors | Windows backslashes must be `\\` in JSON — forward slashes avoid the whole class of bugs |

## Verified on this machine (2026-10-25, OpenCode v2.1.2)

What we actually ran to connect this project — the config above is not
hypothetical, it is the exact `opencode.jsonc` in this directory, and it
works. Two things we learned live:

**1. `opencode mcp add` (v2.1.2) can't pass command flags through `--`.**

```sh
opencode mcp add notes -- uv --directory "E:/..." run notes-server
# ERROR Unrecognized flag: --directory in command opencode mcp add
```

The v2 flag parser rejects arguments like `--directory` even after the `--`
pass-through marker (same error class as the reported `--port` issues
anomalyco/opencode#49085, #50530, #51512). The workaround is the hand-written
config above — which is the documented-by-hand shape anyway. If your command
needs no flags (`npx -y some-server`), `opencode mcp add` still works fine.

**2. Project-level MCP configs ARE detected in V2** (an old V1 issue, #4054,
claimed otherwise) — proven by the connection coming up purely from this
directory's `opencode.jsonc`. OpenCode merges configs walking from the
filesystem root down to the current directory, so this server is visible
whenever OpenCode runs inside this project (use `--global` / the global
config to have it everywhere).

What the connection looked like from the agent's side (Code Mode, the
default): the server's tools appeared as `tools.notes.add_note(...)`,
`tools.notes.search_notes(...)` etc. (the `<server>.<tool>` grouping
predicted above), and the server's `instructions` were injected into the
agent's context inside `<mcp_instructions>` — the live agent then read the
real database rows and wrote a note through the server, with the structured
`Note` object coming back as typed JSON. The exact behaviors this doc
predicted all verified: naming, instructions injection, real-data reads.

## What you have now, end to end

A server you built with the official SDK v2 → tested in-process with the
SDK's own pattern → driven live over stdio by your own client → and finally
connected to a real agent host. The next server you build — for a real API,
a company database, your calendar — changes *only* the `db.py` layer.
