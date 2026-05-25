# pickled-data

**pickled-data** parses SQL migrations (sqlglot), applies them to an in-memory
SQLite sandbox, and runs drift / data-contract gates.

## Status

Pre-alpha v0.1 — dbt models raise `NotImplementedError` (planned v0.2).

## CLI

```bash
uv run pickled-data parse migrations/001.sql
uv run pickled-data apply migrations/001.sql
uv run pickled-data check-drift --migration 001.sql --expected schema.yaml
```

## Cross-contract

Install `pickled-data[cross-contract]` for `DataContractGate` integration with
`pickled_schema.api.SchemaRegistry`.

## MCP tools

| Tool | Description |
|------|-------------|
| `parse_sql_migration` | Parse SQL to AST summary |
| `apply_sql_to_sandbox` | Apply SQL in-memory |
| `check_migration_drift` | Compare migration schema to YAML |
| `draft_sql_migration_from_intent` | Draft SQL DDL from intent |

Mounts as `data_*` on the umbrella `pickled-spec mcp` server.

## Drafting a migration from intent

```bash
pickled-data draft \
  --intent path/to/intent.txt \
  --dialect sqlite \
  --current-schema path/to/schema.yaml
```

Use `-` for `--intent` to read from stdin. LLM cache and budget caps follow
[docs/mcp.md](../../docs/mcp.md).
