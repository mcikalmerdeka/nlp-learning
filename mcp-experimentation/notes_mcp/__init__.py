"""notes_mcp — a Model Context Protocol (MCP) server for a personal notes store.

Package layout (one responsibility per file):

* ``db.py``     — the SQLite data layer. Pure Python, zero MCP imports. This is
                  the "real system" the server connects the model to.
* ``server.py`` — the MCP server itself: an ``MCPServer`` instance with tools,
                  resources, and prompts registered on it, plus the ``main()``
                  entry point behind the ``notes-server`` console script.
"""
