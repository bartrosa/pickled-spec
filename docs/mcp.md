# MCP integration

Each pickled-* package exposes workflows over the [Model Context Protocol](https://modelcontextprotocol.io/)
so tools like Cursor and Claude Desktop can draft artifacts, run gates, and inspect
run telemetry without bespoke UIs.

LLM-backed tools in **pickled-rules**, **pickled-data**, and **pickled-diff** build
clients via `pickled_core.llm.bootstrap.build_default_client`, so they honor the
`cache:` and `budget:` settings in `pickled.config.yaml` (and env overrides) from
the bootstrap PR.

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

## Response cache, budget cap, and model

LLM completions are cached on disk so reruns of `draft_*` and `validate_*`
tools do not re-bill the provider. A budget cap can be installed to abort
LLM calls once a cumulative cost ceiling is reached.
The model used by `complete_prompt`-based drafters is taken from the
provider's `default_model` in `pickled.config.yaml`.

```yaml
providers:
  anthropic:
    type: anthropic
    default_model: claude-sonnet-4-5-20250929   # used by every drafter
    api_key_env: ANTHROPIC_API_KEY
cache:
  dir: .pickled-cache                           # relative paths resolve
  mode: read_write                              # off | read_write | read_only
budget:
  max_cost_usd: "5.00"                          # omit or null for no cap
```

Env overrides (env wins over YAML):

- `PICKLED_CACHE_DIR` — directory for cached JSON entries (CWD-relative)
- `PICKLED_CACHE_MODE` — `off` disables, `read_only` forbids new writes
- `PICKLED_MAX_COST_USD` — decimal string cap
- `PICKLED_LLM_PROVIDER` — pick a provider when multiple are configured

Add `.pickled-cache/` to `.gitignore` if you keep the default location.

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

Tool name prefixes (examples): `bdd_*`, `rules_*`, `schema_*`, `iac_*`, `data_*`, `diff_*`.
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
uv run pickled-diff mcp serve --transport stdio
```

`pickled-bdd serve` remains a **deprecated** alias for `pickled-bdd mcp serve`.

## Tool reference (umbrella prefixes)

| Prefix | Tool | Description |
|--------|------|-------------|
| `rules_` | `list_rules` | List rules from YAML text |
| `rules_` | `check_ruleset_coverage` | Coverage gate over feature texts |
| `rules_` | `draft_ruleset_from_brief` | Draft a YAML rule set from a brief |
| `data_` | `parse_sql_migration` | Parse SQL to AST summary |
| `data_` | `apply_sql_to_sandbox` | Apply SQL in-memory |
| `data_` | `check_migration_drift` | Compare migration schema to YAML |
| `data_` | `draft_sql_migration_from_intent` | Draft SQL DDL from intent |
| `diff_` | `verify_against_oracle` | Differential check (deterministic) |
| `diff_` | `draft_corpus_from_examples` | Expand seed examples into a corpus |
| `iac_` | `draft_terraform_module` | Draft Terraform from a user story |
| `iac_` | `validate_terraform_dir` | Validate Terraform file contents |
| `iac_` | `diff_terraform_plans` | Compare plan JSON |
| `iac_` | `explain_plan_diff` | Summarise plan JSON, flag risky actions |
| `iac_` | `suggest_security_remediation` | Patch hints for Trivy findings |

Other prefixes (`bdd_`, `schema_`) are documented in their package READMEs.

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

Expect at least a dozen tools from the umbrella list (19 with rules/data/diff
draft and iac advisor tools).

## Workspace gates vs MCP tools

`pickled-spec check-all` runs **workspace gate runners** (`pickled.gates` entry
points) over a directory layout (`features/`, `specs/`, `infra/`, `migrations/`).
MCP tools expose finer-grained operations (draft, single gate, parse). Both share
the same underlying gate classes where applicable.

## See also

- [`pattern.md`](pattern.md) — LLM-to-DSL bridge
- [`gates.md`](gates.md) — compensating gates exposed as tools
- [`integration-example.md`](integration-example.md) — end-to-end example
