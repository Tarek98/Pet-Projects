# Day 2 — Minimal MCP server (HR-style tools)

A small [Model Context Protocol](https://modelcontextprotocol.io) server that exposes HR-style tools. Use this to learn MCP and test with **MCP Inspector** or Cursor.

## Setup

```bash
# From Workday-AI-Agent-Prep/starter_project
pip install "mcp[cli]"
# or: uv add "mcp[cli]"
```

## Run

```bash
# From this directory (mcp_server_hr)
uv run hr_server.py
# or: python hr_server.py
```

Then in another terminal, use [MCP Inspector](https://github.com/modelcontextprotocol/inspector) to connect to the server (stdio) and call the tools.

## Cursor

You can add this server to Cursor's MCP config so the AI can use these tools when you work in this repo. See [MCP docs](https://modelcontextprotocol.io/docs/develop/build-server) for host configuration.
