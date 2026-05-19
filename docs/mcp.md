# MCP integration

Each pickled-* package exposes workflows over the [Model Context Protocol](https://modelcontextprotocol.io/)
so tools like Cursor and Claude Desktop can draft Gherkin, run gates, and inspect
run telemetry without bespoke UIs.

## Install

From the monorepo root:

```bash
uv sync --extra mcp
```

Or install the extra on `pickled-core`:

```bash
pip install 'pickled-core[mcp]'
```

Dependencies: `mcp>=1.27.1`, `fastmcp>=3.3.1,<4.0`.

## Stdio hygiene

On **stdio** transport, the MCP server must use **stdout only for JSON-RPC**
messages. All logging goes to **stderr** (`pickled_core.mcp.stdio_logging` configures
this before `FastMCP.run()`).

If a client reports a corrupted stream, check stderr for accidental `print()` or
logging to stdout.

## Per-package servers

```bash
# BDD: draft + ambiguity gate
uv run pickled-bdd mcp serve --transport stdio

# Rules: coverage gate + list rules
uv run pickled-rules mcp serve --transport stdio
```

HTTP (streamable HTTP) is available for local testing:

```bash
uv run pickled-bdd mcp serve --transport http --host 127.0.0.1 --port 7801
```

Binding `0.0.0.0` requires an explicit safety flag:

```bash
uv run pickled-spec mcp --transport http --host 0.0.0.0 --allow-public
```

`pickled-bdd serve` remains as a **deprecated** alias for `pickled-bdd mcp serve`.

## Umbrella server

One process mounts every package that registers a `pickled.mcp.subservers` entry point:

```bash
uv run pickled-spec mcp --transport stdio
```

Mounted namespaces (examples): `bdd_*`, `rules_*` tools; core resources under
`pickled://runs`, `pickled://config`.

## Cursor configuration

Replace `/ABSOLUTE/PATH/TO/pickled-spec` with your clone path:

```json
{
  "mcpServers": {
    "pickled-spec": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/ABSOLUTE/PATH/TO/pickled-spec",
        "--extra",
        "mcp",
        "pickled-spec",
        "mcp"
      ]
    }
  }
}
```

File: `~/.cursor/mcp.json` (or project MCP settings, depending on Cursor version).

## Claude Desktop configuration

Same JSON shape. Platform paths:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

After editing, **fully quit** Claude Desktop (Cmd+Q on macOS) and reopen so the
server restarts.

## Resources

| URI | Content |
|-----|---------|
| `pickled://runs` | JSON list of run IDs under `PICKLED_RUNS_DIR` (default `./runs`) |
| `pickled://runs/{run_id}/manifest` | ADR-0004 whitelisted manifest |
| `pickled://runs/{run_id}/llm_calls/{limit}` | Last *limit* lines from `llm_calls.jsonl` |
| `pickled://config` | Current `pickled.config.yaml` or redacted provider summary |

## Money fields

Cost fields in tool outputs use **decimal strings** (e.g. `"0.0123"`), not JSON
numbers, matching the Week 2 pricing convention.

## Smoke test

```bash
uv run python scripts/smoke_mcp_stdio.py
```

## See also

- [`pattern.md`](pattern.md) — LLM-to-DSL bridge
- [`gates.md`](gates.md) — compensating gates exposed as tools
