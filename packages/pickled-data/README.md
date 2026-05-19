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

## MCP

Mounts as `data_*` on the umbrella `pickled-spec mcp` server.
