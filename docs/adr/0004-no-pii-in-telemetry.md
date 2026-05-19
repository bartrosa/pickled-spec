# ADR-0004: No PII in telemetry manifests

## Status

Accepted — 2026-05-19

## Context

`pickled-core` writes run directories under `runs/<run_id>/` with a
`manifest.json` and append-only `llm_calls.jsonl`. Some runs are published as
public audit trails on bartrosa.dev; the same code path also serves private
projects such as a private task tracker. Telemetry must never embed
identifying information that could deanonymize a contributor or their machine.

## Decision

`manifest.json` may contain **only** the following keys. The writer enforces
this whitelist programmatically; extra keys are rejected at write time.

| Key | Purpose |
|-----|---------|
| `run_id` | Opaque run identifier (ULID) |
| `config_sha256` | Hash of the resolved LLM config file |
| `pricing_sha256` | Hash of the bundled `pricing.yaml` |
| `git_sha` | Repository commit (if available) |
| `hostname_truncated_8` | First 8 characters of machine hostname |
| `python_version` | `major.minor.micro` only |
| `created_at_utc` | ISO-8601 UTC timestamp |

### Field blacklist (must never appear)

The manifest writer and tests must never read or persist:

- `git config user.email`, `git config user.name`
- `whoami`, `USER`, `USERNAME`, `HOME`
- Absolute filesystem paths
- Raw environment variables (`os.environ[...]` for manifest values)
- Full hostname (only the truncated prefix above)
- Any string longer than 64 characters sourced from the environment

Rationale: public audit trails must not leak personal information; private
runs benefit from the same conservative defaults.

## Consequences

### Positive

- One code path for public and private runs; reviewers can grep for forbidden
  patterns in `pickled_core/telemetry/`.
- Manifest schema stays small and stable for downstream tooling.

### Negative

- Debugging a run from manifest alone omits operator identity (by design).
- `git_sha` may be empty outside a git checkout.

### Neutral

- `llm_calls.jsonl` records model usage and costs but not prompts; prompt
  content is out of scope for this ADR.
