# User management CRUD — integration example

This workspace demonstrates the full pickled-* loop on a single domain: a
user account API with registration, access, rectification, portability, and
erasure. Five packages exercise the same artefacts from different angles.

## Layout

| Path | Package | Role |
|------|---------|------|
| `features/` | pickled-bdd | Gherkin scenarios and parse checks |
| `specs/openapi.yaml` | pickled-schema | API contract + `@schema:endpoint:*` coverage |
| `infra/` | pickled-iac | Terraform module (validate + optional Trivy) |
| `migrations/` | pickled-data | SQL DDL + drift vs `expected_schema.yaml` |
| `pickled.ruleset.yaml` | pickled-rules | Points at `gdpr-web-crud` (25 rules) |

## Dogfooding loop

1. **pickled-bdd** parses every `.feature` file under `features/`. With an LLM
   configured, AmbiguityGate can review scenarios; `check-all` skips it by
   default and records a PASS with a skip note.
2. **pickled-schema** validates `specs/openapi.yaml` and runs SchemaCoverageGate
   so each `@schema:endpoint:METHOD-/path` tag has a matching OpenAPI path.
3. **pickled-iac** runs `terraform validate` on `infra/`. Trivy config scan runs
   when installed; otherwise the security gate passes with a skip note.
4. **pickled-data** parses `migrations/001_users_soft_delete.sql`, applies it to
   an in-memory SQLite sandbox, and compares the result to `expected_schema.yaml`.
5. **pickled-rules** loads `gdpr-web-crud` and runs CoverageGate on all
   features. Every **strict** rule must be cited at least once via
   `@gdpr-web-crud:<rule_id>` tags.

## Commands

From the monorepo root:

```bash
# Exit 0 when Terraform/LLM are not installed (optional WARN rows only):
uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok

uv run pickled-rules check \
  --ruleset packages/pickled-rules/rulesets/examples/gdpr-web-crud.yaml \
  --feature-glob 'examples/user-management-crud/features/**/*.feature'

uv run pickled-schema check \
  --spec specs/openapi.yaml \
  --feature-dir features

uv run pickled-data check-drift \
  --migration migrations/001_users_soft_delete.sql \
  --expected expected_schema.yaml \
  --dialect sqlite
```

Run these from the monorepo root (adjust paths) or from this directory for
`pickled-schema` / `pickled-data` commands.

## Cursor MCP

Point Cursor at the monorepo with the umbrella server (replace the path):

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

## Scenario focus

The deletion flow in `delete_user_account.feature` walks through
subject-initiated erasure: soft-delete, retention window, audit logging, and
410 Gone on subsequent reads — aligned with erasure and storage-limitation
rules in the `gdpr-web-crud` rule set.
