# Integration example: user-management-crud

The canonical end-to-end workspace lives at
[`examples/user-management-crud/`](../examples/user-management-crud/).

It ties together all five leaf packages on one fictional product: a CRUD API
for user accounts with registration, subject access, rectification, data export,
and account deletion.

## Prerequisites

```bash
uv sync --extra mcp
```

Optional but useful:

- `terraform` or `tofu` on PATH — enables pickled-iac validate in `check-all`
- `trivy` on PATH — optional config scan on `infra/` (skipped gracefully if absent)
- `openapi-spec-validator` — installed via `pickled-schema[openapi]` in the workspace

## One-shot verification

```bash
uv run pickled-spec check-all --workdir examples/user-management-crud/
```

Use `--warn-ok` for exit code 0 when only optional tools are missing (no
Terraform/tofu on PATH, and similar WARN rows):

```bash
uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok
```

`check-all` runs **workspace gates** registered under the `pickled.gates` entry
point group (parse, coverage, validate, drift, security scan). It does not yet
invoke every gate class in each package (for example PlanDiffGate or
DataContractGate).

### Expected output shape

```text
package  gate                              verdict  findings  notes
-------  --------------------------------  -------  --------  -----
bdd      bdd.parse.delete_user_account     pass     0         parsed features/...
bdd      bdd.ambiguity                     pass     0         skipped — set PICKLED_BDD_LLM_FACTORY …
rules    rules.coverage                    pass     0         All strict rules in gdpr-web-crud …
schema   schema.openapi.validate.openapi.yaml pass  0         specs/openapi.yaml
schema   schema.coverage                   pass     0         All @schema:endpoint tags …
iac      iac.validate                      warn     0         terraform/tofu missing (optional)
iac      iac_security_baseline             pass     0         No HIGH or CRITICAL findings.
data     data.parse.001_users_soft_delete.sql pass 0        parsed
data     data.migration_drift              pass     0         Schema matches expected.
```

Exit codes: `0` all pass (or all pass/WARN with `--warn-ok`), `1` if any WARN
(and no FAIL) without `--warn-ok`, `2` if any FAIL.

## Per-package commands

### Rules coverage (gdpr-web-crud)

```bash
uv run pickled-rules list-rules \
  --ruleset packages/pickled-rules/rulesets/examples/gdpr-web-crud.yaml

uv run pickled-rules check \
  --ruleset packages/pickled-rules/rulesets/examples/gdpr-web-crud.yaml \
  --feature-glob 'examples/user-management-crud/features/**/*.feature'
```

`--feature-glob` with multiple files uses **union** coverage: all 20 **strict**
rules must appear at least once across the set, not in every file.

### Schema

```bash
uv run pickled-schema validate examples/user-management-crud/specs/openapi.yaml

uv run pickled-schema check \
  --spec examples/user-management-crud/specs/openapi.yaml \
  --feature-dir examples/user-management-crud/features
```

`--feature-glob` is an alias for the same check.

### Data drift

```bash
uv run pickled-data check-drift \
  --migration examples/user-management-crud/migrations/001_users_soft_delete.sql \
  --expected examples/user-management-crud/expected_schema.yaml \
  --dialect sqlite
```

The integration example oracle uses SQLite; nullable-only differences versus
YAML (for example `DEFAULT now()` → `NOT NULL`) are reported as pass with a
note, not a hard fail.

## Cursor MCP

Use the umbrella server from the repo root so tools from bdd, rules, schema, iac,
and data are available under one process:

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

Replace `/ABSOLUTE/PATH/TO/pickled-spec` with your clone path. Restart Cursor
after editing the config.

## Rule set

`packages/pickled-rules/rulesets/examples/gdpr-web-crud.yaml` defines 25 rules
for typical web CRUD systems. Article references appear only in each rule's
`description` field. The integration example cites strict rules via Gherkin tags
such as `@gdpr-web-crud:right-to-erasure`.
