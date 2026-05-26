# Story: pickled-bdd drafts a Gherkin feature from a user story

## Context

A developer (or an agent acting on their behalf) starts with a short
natural-language description of a behaviour — "as a user I want to reset
my password by clicking a link in email", "registered users can export
their data as JSON" — and wants a draft Gherkin feature file they can
review, tag, and check in. The drafter is the entry point for everyone
new to pickled-spec: it produces the first artifact, and that artifact
is what every downstream gate (coverage, ambiguity, schema, drift)
will inspect.

The drafter sits behind two surfaces. Engineers call it from the CLI
as `pickled-bdd draft`. Agents (Cursor, Claude Desktop) call the same
core via the MCP tool `bdd_draft_feature_from_story`. Both paths must
behave identically, because dogfooding assumes the agent path is a
first-class citizen, not a thin wrapper over a "real" CLI.

## What pickled-spec does today

`FeatureDrafter.draft_from_story(story_text)` runs one LLM completion
with temperature 0 and a prompt that asks for a Feature header, a brief
narrative, and three to seven scenarios in canonical Given-When-Then
form. The drafter validates the LLM's output by parsing it with the
pytest-bdd adapter; if parsing fails, the failure goes into the
`warnings` field rather than raising an exception, and the raw text is
returned anyway so the caller can fix it.

The MCP tool returns a fixed JSON shape:
`{feature_text, rationale, warnings, model_used}`. The model is
resolved from `pickled.config.yaml` via `build_default_client`, so the
same configuration that drives every other LLM-backed tool drives this
one. Identical inputs hit the disk cache and do not re-bill the
provider. A configured budget cap (via YAML or `PICKLED_MAX_COST_USD`)
applies.

The drafter does not auto-tag scenarios with rule references. Tagging
is a deliberate downstream human (or agent) step, because the choice
of which rule a scenario implements is the kind of decision pickled-spec
explicitly refuses to make on the user's behalf.

## What we want to verify

The drafter behaves as a deterministic, observable, parsing-validated
producer of Gherkin. Specifically, across the CLI and MCP surfaces:

- A well-formed story yields a feature whose text starts with
  `Feature:`, parses cleanly through the pytest-bdd adapter, and comes
  back with `warnings: []`.
- An empty or whitespace-only story yields a deterministic failure
  shape — either a typed error before the LLM call, or a populated
  `warnings` list — never a partial unparseable feature.
- Identical story text submitted twice in the same session results in
  exactly one billable LLM call; the second call comes from cache and
  returns byte-identical output.
- The model used is the one named in `pickled.config.yaml`, not the
  hardcoded fallback in `complete_prompt` (regression guard for the
  bug ADR-0005 fixed).
- Temperature is zero on every call, regardless of how the caller
  invokes the tool.
- Output JSON shape is exactly the four keys above; no extra fields
  leak through when the underlying provider returns additional
  metadata.

## Inventory references

- CLI: `pickled-bdd draft --story <PATH|->`
- MCP tools: `bdd_draft_feature_from_story`
- Gates: `FeatureDrafter` (class in `pickled_bdd.drafter`), the
  pytest-bdd adapter used for post-validation
- ADRs: ADR-0005 (cache, budget, model resolution)

## Open questions

- Should `warnings` distinguish between "parser failed" and "LLM
  emitted no scenarios"? Today they collapse into a single list of
  strings; consumers cannot programmatically tell which class of
  problem they have. Candidate for a future typed-error refinement
  tracked under `llm-failure-modes-typed-not-stringly`.
- Is "exactly one billable call on cache hit" testable via the public
  API, or do we need to expose a cache-hit counter? Today we would
  have to assert by introspecting the cache directory size, which is
  brittle.

## Status

draft
