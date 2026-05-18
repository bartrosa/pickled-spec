# pickled-rules

**Rule coverage gate for project artifacts.**

Loads YAML rule sets and verifies that Gherkin features cite the rules that
apply to them. Think of it as test coverage, but for the rules your team — not
the language — chose to enforce.

## Example rule set

```yaml
metadata:
  source_id: "TEAM-API-CONV"
  source_title: "Backend Team API Conventions"
  applies_to: "backend-services"
  maintainer: "Backend Platform Team"
  source_version: "1.2"
  active_from: "2025-09-01"
rules:
  - id: "naming.1"
    title: "Resource paths are plural nouns"
    description: "REST resource collections use plural lowercase nouns."
    enforcement: "strict"
  - id: "naming.2"
    title: "Version prefix is mandatory"
    description: "All public endpoints live under /v{N}/."
    enforcement: "strict"
```

## Tags in feature files

Reference rules with `@<ruleset>:<rule_id>` on scenarios (or on the feature,
inherited by every scenario):

```gherkin
@team-api-conv:naming.1
Scenario: List users returns a versioned path
  Given the API is running
  When I GET /v1/users
  Then the response status is 200
```

## CLI

```bash
pickled-rules check \
  --ruleset team-api-conv \
  --feature features/orders.feature
```

Built-in rule sets: `team-api-conv`, `review-checklist`. Pass a file path instead
of a name for custom YAML.

## What v0.1 ships

- YAML rule set loader and schema validation
- Two example built-in rule sets
- Coverage gate (strict rules must be referenced; unknown tags fail)
- Markdown and JSON coverage reports
- `pickled-rules check` CLI

## What v0.1 does not ship

- Solver-backed gates
- Conflict detection across rule sets
- Drift detection when `source_version` changes
- Additional built-in rule sets beyond the examples

## Roadmap and rationale

- [Roadmap section](../../docs/roadmap.md#pickled-rules--rule-coverage-analysis)
- [ADR-0003](../../docs/adr/0003-merge-into-pickled-rules.md) — why this package
  exists as generic rule coverage tooling

## License

Apache-2.0.
