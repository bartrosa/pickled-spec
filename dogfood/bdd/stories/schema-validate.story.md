# Story: pickled-schema validates OpenAPI documents and tag coverage

## Context

An API has two specifications: the human-language behaviour
description (Gherkin features) and the machine-language interface
description (OpenAPI document). When these two drift apart, both
sides claim to be correct and the running code is silently wrong.
The classic failure: a feature describes a `DELETE /users/{id}`
behaviour, the OpenAPI doc only mentions `GET` and `POST` for that
path, and nobody notices until production.

`pickled-schema` exists to keep the two synchronised. It validates
the OpenAPI document itself against the 3.x specification (so the
document is not internally broken), and it computes coverage between
feature tags and OpenAPI paths (so every documented endpoint is
behaviour-tested and every feature points at a real endpoint).

This is the deterministic half of pickled-spec. There is no LLM in
the validation path; correctness is a function of the input
document, the OpenAPI grammar, and the `openapi-spec-validator`
library. Coverage is also fully deterministic — it is a set
operation between feature tags of shape `@schema:endpoint:METHOD-/path`
and paths declared in the OpenAPI doc.

## What pickled-spec does today

`pickled-schema validate <path>` runs `openapi-spec-validator` on a
YAML or JSON OpenAPI document and reports the first validation error
or PASS if clean. The workspace gate
`schema.openapi.validate.<filename>` does the same for every
`*.yaml` and `*.json` file under `specs/` in a workspace.

`pickled-schema check --spec <path> --feature-dir <dir>` (alias:
`--feature-glob`) runs the coverage gate `schema.coverage`. It parses
every feature, extracts tags matching the `@schema:endpoint:METHOD-/path`
shape (case-insensitive on the method, exact on the path), and
compares to the path/method pairs declared in the OpenAPI document.
Verdicts:

- PASS: every method/path declared in the OpenAPI doc has at least
  one feature tag pointing at it.
- FAIL: at least one method/path is missing a tag, or at least one
  tag points at a method/path not in the OpenAPI doc.

The MCP surface is `schema_validate_openapi` and `schema_check_coverage`.

When the workspace `pickled.ruleset.yaml` declares no OpenAPI doc
in `specs/`, the schema gates emit WARN with a note `no OpenAPI
specs found` rather than failing — a workspace can legitimately
exercise other gates without owning an API.

## What we want to verify

Across the CLI and MCP surfaces:

- A syntactically valid OpenAPI 3.0 or 3.1 document yields PASS on
  `schema.openapi.validate.<filename>`.
- A document with a missing required field (e.g. `info.version`)
  yields FAIL whose notes contain the JSON pointer to the missing
  field, sourced from `openapi-spec-validator`.
- A document containing a `$ref` cycle (path A references B
  references A) yields a deterministic FAIL — not an infinite loop
  or a stack overflow — even if no validator natively handles it.
- A feature carrying `@schema:endpoint:GET-/users/{id}` and an
  OpenAPI doc declaring exactly that operation yields PASS coverage.
- A feature tag pointing at a path or method not declared in the
  OpenAPI doc yields FAIL with the offending tag named in the
  notes.
- An OpenAPI doc declaring an operation that no feature references
  yields FAIL with the offending method/path named.
- Method matching is case-insensitive on tags (so `GET-/users` and
  `get-/users` are equivalent), and path matching is exact
  (`/users/{id}` and `/users/{userId}` are not equivalent, even if
  both refer to the same path template).
- A workspace with no `specs/*.{yaml,json}` files yields WARN with
  a clear `no OpenAPI specs found` note, not FAIL.

## Inventory references

- CLI: `pickled-schema validate <PATH>`,
  `pickled-schema check --spec <X> --feature-dir <Y>`
- MCP tools: `schema_validate_openapi`, `schema_check_coverage`
- Gates: `schema.openapi.validate.<filename>` (entry point name),
  `schema.coverage` (entry point name)
- ADRs: none directly applicable (schema dates back to v0.1)

## Open questions

- Path-template equivalence is currently exact-string. `GET /users/{id}`
  and `GET /users/{userId}` are different paths even though they have
  the same RFC 6570 shape. This is arguably a bug — two equally
  RFC-compliant ways of writing the same template should produce
  identical coverage. Today the user has to align their feature tags
  exactly to the OpenAPI parameter names. Tracked under
  `path-templating-rfc-6570-compliant`.
- The validator only catches first-order errors (the document is
  malformed). It does not catch second-order errors (the document
  is well-formed but semantically wrong, e.g. a `200` response
  schema that declares a property the implementation never sends).
  Catching the second order is out of scope for v0.3 but is
  exactly the territory where an LLM advisor tool would help —
  candidate for a `schema_explain_diff` advisor mirroring the
  approach `iac_explain_plan_diff` takes for Terraform.
- WARN-vs-FAIL on a missing `specs/` directory is policy. Today we
  WARN; consistency with the AmbiguityGate's "PASS with note when
  skipped" would suggest WARN is too loud. Candidate to revisit
  alongside `verifier-warn-not-fail-on-skippable`.

## Status

draft
