# MCP integration

Each pickled-* package exposes workflows over the [Model Context Protocol](https://modelcontextprotocol.io/)
so tools like Cursor and Claude Desktop can draft artifacts, run gates, and inspect
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

## Umbrella server (recommended)

One process mounts every package that registers a `pickled.mcp.subservers` entry point:

```bash
uv run pickled-spec mcp --transport stdio
```

Tool name prefixes (examples): `bdd_*`, `rules_*`, `schema_*`, `iac_*`, `data_*`.
Core resources: `pickled://runs`, `pickled://config`.

HTTP for local testing:

```bash
uv run pickled-spec mcp --transport http --host 127.0.0.1 --port 7800
```

Binding `0.0.0.0` requires `--allow-public`.

## Per-package servers

Use these when you only need one domain:

```bash
uv run pickled-bdd mcp serve --transport stdio
uv run pickled-rules mcp serve --transport stdio
uv run pickled-schema mcp serve --transport stdio
uv run pickled-iac mcp serve --transport stdio
uv run pickled-data mcp serve --transport stdio
uv run pickled-diff serve
```

`pickled-diff` exposes **`verify_against_oracle`** (deterministic; no LLM). It is
not yet mounted on the umbrella server; use the package `serve` command or register
tools in-process until a `pickled.mcp.subservers` entry is added.

`pickled-bdd serve` remains a **deprecated** alias for `pickled-bdd mcp serve`.

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
        "mcp",
        "--transport",
        "stdio"
      ]
    }
  }
}
```

File: `~/.cursor/mcp.json` (or project MCP settings, depending on Cursor version).

Point the workspace at an example directory when dogfooding:
[`examples/user-management-crud/`](../examples/user-management-crud/) — see
[`integration-example.md`](integration-example.md).

## Claude Desktop configuration

Same JSON shape. Platform paths:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

After editing, **fully quit** Claude Desktop and reopen so the server restarts.

## Resources

| URI | Content |
|-----|---------|
| `pickled://runs` | JSON list of run IDs under `PICKLED_RUNS_DIR` (default `./runs`) |
| `pickled://runs/{run_id}/manifest` | ADR-0004 whitelisted manifest |
| `pickled://runs/{run_id}/llm_calls/{limit}` | Last *limit* lines from `llm_calls.jsonl` |
| `pickled://config` | Current `pickled.config.yaml` or redacted provider summary |

## Money fields

Cost fields in tool outputs use **decimal strings** (e.g. `"0.0123"`), not JSON
numbers.

## Smoke test

```bash
uv run python scripts/smoke_mcp_stdio.py
```

Expect at least a dozen tools from the umbrella list.

## Workspace gates vs MCP tools

`pickled-spec check-all` runs **workspace gate runners** (`pickled.gates` entry
points) over a directory layout (`features/`, `specs/`, `infra/`, `migrations/`).
MCP tools expose finer-grained operations (draft, single gate, parse). Both share
the same underlying gate classes where applicable.

## See also

- [`pattern.md`](pattern.md) — LLM-to-DSL bridge
- [`gates.md`](gates.md) — compensating gates exposed as tools
- [`integration-example.md`](integration-example.md) — end-to-end example
