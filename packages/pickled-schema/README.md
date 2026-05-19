# pickled-schema

**pickled-schema** is the schema-focused member of the **pickled-\*** family: an
**LLM-to-OpenAPI / JSON Schema / Protobuf** bridge with compensating gates for
ambiguity and Gherkin tag coverage.

## Status

Pre-alpha v0.1 — **OpenAPI 3.x** is fully implemented (parse, validate, draft,
coverage gate, MCP). **JSON Schema** has parser + meta-validator only.
**Protobuf** has parser-only via `grpc_tools.protoc`. Runtime request/response
validation (`openapi-core`) is planned for v0.3 (DriftGate).

## Supported formats

| Format | Parse | Validate | Draft (LLM) |
|--------|-------|----------|-------------|
| OpenAPI 3.0 / 3.1 / 3.2 | yes | yes (`openapi-spec-validator`) | yes (3.1 path items) |
| JSON Schema Draft 2020-12 | yes | meta-validation only | v0.2 (planned) |
| Protobuf proto3 | yes (descriptor set) | protoc exit code only | v0.2+ (planned) |

OpenAPI **2.0 (Swagger)** is rejected in v0.1.

## Development (from the monorepo)

```bash
uv sync
cd packages/pickled-schema && uv pip install -e ".[all-formats]" && cd ../..
uv run pytest packages/pickled-schema -v
uv run ruff check packages/pickled-schema
uv run mypy --strict packages/pickled-schema/src
```

Optional extras: `[openapi]`, `[json-schema]`, `[proto]`, `[all-formats]`, `[mcp]`.

## CLI

Console script: **`pickled-schema`**.

```bash
uv run pickled-schema --help
```

| Command | Purpose |
|---------|---------|
| **`parse <file>`** | Parse a schema file; print format summary JSON. |
| **`validate <file>`** | Structural validation for the detected format. |
| **`draft`** | Draft an OpenAPI 3.1 path item from a Gherkin file (`--method`, `--path`, `--gherkin-file`, `-o`). |
| **`check`** | Run `SchemaCoverageGate` (`--spec`, `--feature-dir`). |
| **`mcp serve`** | Start the MCP server (stdio or HTTP). |

### Examples

```bash
uv run pickled-schema parse \
  packages/pickled-schema/tests/fixtures/openapi/users-crud.yaml

uv run pickled-schema validate \
  packages/pickled-schema/tests/fixtures/openapi/users-crud.yaml

uv run pickled-schema check \
  --spec packages/pickled-schema/tests/fixtures/openapi/users-crud.yaml \
  --feature-dir path/to/features
```

### LLM backend

Draft and ambiguity gates need an **`LLMClient`**. Configure `pickled.config.yaml`
and provider API keys, or set **`PICKLED_SCHEMA_LLM_FACTORY=module:callable`**
for tests.

## Gherkin tags (coverage gate)

Scenarios can declare expected endpoints:

```gherkin
@schema:endpoint:POST-/users
Scenario: Create a user
  When I POST to /users
```

`SchemaCoverageGate` fails if the OpenAPI spec has no matching
`paths["/users"]["post"]`.

## MCP tools

Registered on the umbrella server as **`schema_*`** (namespace `schema`):

| Tool | Description |
|------|-------------|
| `draft_openapi_endpoint` | Draft path item YAML from Gherkin text |
| `validate_openapi_spec` | Validate OpenAPI YAML |
| `check_schema_coverage` | Match `@schema:endpoint:*` tags in feature texts |

```bash
uv run pickled-schema mcp serve --transport stdio
```

See monorepo [`docs/mcp.md`](../../docs/mcp.md) for Cursor / Claude Desktop setup.

## Cross-package contract

`pickled_schema.api.SchemaRegistry` defines `find_schema_by_tag(tag) -> SchemaArtifact | None`.
**pickled-data** (Week 5) will implement this against a schema store.

## What is NOT in v0.1

- JSON Schema LLM drafter
- Protobuf validator beyond protoc
- Bundled `protoc` binary (uses `python -m grpc_tools.protoc`)
- Request/response runtime validation (`openapi-core` / DriftGate)
- OpenAPI 2.0 support

## License

Apache-2.0 — see repository root `LICENSE`.
