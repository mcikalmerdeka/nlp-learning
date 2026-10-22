"""A scripted MCP *client* that talks to our notes server the way real hosts do.

Run it with:

    uv run client.py

What this demonstrates, step by step
------------------------------------
A "host" (OpenCode, Claude Desktop, an IDE) is a program that launches an MCP
server as a child process and speaks JSON-RPC to it over stdin/stdout. The
SDK's unified ``Client`` does exactly that when you hand it
``StdioServerParameters`` instead of a URL — so this file is a miniature host:
same lifecycle, same verbs, just no LLM in the loop yet.

Three behaviors to notice while it runs:

1. **The client owns the child's lifecycle.** Entering ``async with`` spawns
   the server; leaving the block shuts it down (close stdin, wait, kill if it
   lingers). We never manage the process ourselves.
2. **The child does NOT inherit our environment.** SDK v2 gives a launched
   server a minimal allow-list (HOME/LOGNAME/PATH/SHELL/TERM/USER on POSIX).
   Secrets or settings must be passed explicitly via ``env=`` — ours needs
   none, because the DB location is baked into the package (see db.py).
3. **stdout on the client side is normal console output.** The "never print
   to stdout" rule binds the SERVER (stdout is its protocol stream). The
   client's stdout carries only these readable lines.
"""

from __future__ import annotations

import sys
from pathlib import Path

import anyio
from mcp import Client, StdioServerParameters
from mcp.types import TextContent, TextResourceContents

# Resolve OUR directory (not cwd) so the demo works from anywhere. The
# --directory flag makes uv run the server inside the project directory,
# which is what a host config file does (docs/05-connecting-opencode.md).
PROJECT_ROOT = Path(__file__).resolve().parent

SERVER = StdioServerParameters(
    command="uv",
    args=["run", "--directory", str(PROJECT_ROOT), "notes-server"],
)

failures: list[str] = []


def check(label: str, ok: bool) -> bool:
    """Record and display one expectation. Light assertions keep the script a
    readable walkthrough first and a test second."""
    print(f"    [{ 'PASS' if ok else 'FAIL' }] {label}")
    if not ok:
        failures.append(label)
    return ok


def banner(step: int, title: str) -> None:
    print(f"\n=== STEP {step}: {title} " + "=" * max(0, 60 - len(title)))


async def main() -> None:
    # ---------------------------------------------------------------- enter
    banner(1, "connect (the initialize handshake)")
    # Constructing Client(SERVER) only describes the transport; entering the
    # async-with block spawns the subprocess and negotiates the protocol.
    async with Client(SERVER) as client:
        print(f"    server name:    {client.server_info.name}")
        print(f"    server version: {client.server_info.version}")
        print(f"    protocol:       {client.protocol_version}")
        print(f"    capabilities:   {client.server_capabilities}")
        print(f"    instructions:   {client.instructions[:72]}...")
        check(
            "handshake reports a notes server",
            client.server_info.name == "notes",
        )

        # ------------------------------------------------------------ tools
        banner(2, "list_tools (what the model would see)")
        tools = (await client.list_tools()).tools
        for tool in tools:
            description = (tool.description or "").split("\n")[0]
            print(f"    - {tool.name}: {description}")
        check("four tools exposed", len(tools) == 4)

        banner(3, "list resources (concrete) and resource templates")
        concrete = (await client.list_resources()).resources
        templates = (await client.list_resource_templates()).resource_templates
        for resource in concrete:
            print(f"    resource:  {resource.uri}")
        for template in templates:
            print(f"    template:  {template.uri_template}")
        check(
            "notes://stats concrete, note://{id} template",
            any(str(r.uri) == "notes://stats" for r in concrete)
            and any(t.uri_template == "note://{id}" for t in templates),
        )

        banner(4, "call_tool: add_note -> structured output")
        added = await client.call_tool(
            "add_note",
            {
                "title": "Created by client.py",
                "content": "This row exists because a CLIENT called a TOOL.",
                "tags": ["demo"],
            },
        )
        structured = added.structured_content
        print(f"    is_error:           {added.is_error}")
        print(f"    text for the model: {structured and structured['title']}")
        print(f"    structured for code: {structured}")
        check("added note came back with an id", structured and structured["id"] > 0)
        note_id = structured["id"]

        banner(5, "read_resource: the note we just created")
        contents = (await client.read_resource(f"note://{note_id}")).contents
        text = "".join(c.text for c in contents if isinstance(c, TextResourceContents))
        print(text)
        check("resource read returns the stored row", "Created by client.py" in text)

        banner(6, "call_tool: search_notes (reads the REAL database)")
        result = await client.call_tool("search_notes", {"query": "welcome"})
        print("\n".join(f"    {line}" for line in _text(result).splitlines()))
        check(
            "search finds the seeded note from disk",
            result.is_error is False and "- #" in _text(result),
        )

        banner(7, "call_tool: delete_note(999) -> a deliberate FAILURE")
        # Expected failures travel as is_error=True with the message as text
        # the MODEL can read and react to (not a raised exception!).
        result = await client.call_tool("delete_note", {"note_id": 999})
        print(f"    is_error: {result.is_error}")
        print(f"    model reads: {_text(result)}")
        check(
            "missing id => is_error=True with readable message",
            result.is_error is True and "not found" in _text(result),
        )

        banner(8, "get_prompt: summarize_notes renders a ready-to-send message")
        rendered = await client.get_prompt("summarize_notes", {"query": "mcp"})
        message = rendered.messages[0]
        print(f"    role: {message.role}")
        print(f"    text: {message.content.text[:100]}...")
        check("prompt rendered a user message", message.role == "user")

        banner(9, "read_resource: notes://stats (aggregates the real DB)")
        contents = (await client.read_resource("notes://stats")).contents
        stats_text = "".join(
            c.text for c in contents if isinstance(c, TextResourceContents)
        )
        print(stats_text)
        # Parse the COUNT, don't substring-match it: 'Total notes: 20' contains
        # 'Total notes: 2', which would false-fail the check from the 18th run on.
        count_line = stats_text.splitlines()[0]  # "Total notes: 3"
        count = int(count_line.rsplit(" ", 1)[1])
        # 2 seeded + the one this run created
        check("stats count >= 3", count >= 3)

    # ------------------------------------------------------------- leave
    # The `async with` block ending here closed the child process.
    print()
    if failures:
        print(f"FAILED CHECKS ({len(failures)}): " + ", ".join(failures))
        raise SystemExit(1)
    print("ALL CHECKS PASSED")


def _text(result) -> str:
    return "\n".join(
        block.text for block in result.content if isinstance(block, TextContent)
    )


if __name__ == "__main__":
    anyio.run(main)
