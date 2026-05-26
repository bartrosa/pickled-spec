# Story: pickled-rules drafts a ruleset YAML from a natural-language brief

## Context

A team has informal conventions that live in Slack threads, code review
comments, and one engineer's head. Turning that tribal knowledge into
an enforceable ruleset is friction: you have to learn the YAML schema,
invent rule IDs, pick enforcement levels, and write descriptions that
will survive being read in twelve months by someone who wasn't there.

The drafter compresses that friction. The user pastes a brief — "we
want our internal APIs to use plural noun paths, require explicit
versioning, return RFC 7807 error bodies, and document every endpoint"
— along with the metadata pickled-rules requires (`source_id`,
`applies_to`, `active_from`). The drafter emits a syntactically valid
YAML ruleset that loads cleanly through `load_ruleset_from_text`, with
neutral terminology, kebab-case IDs, and a structured rationale.

The drafter is positioned as a **starting point**, not a finished
artefact. Output goes into the editor; the human reviews, renames,
splits, merges, retunes enforcement levels. The drafter's job is to
remove the cold-start cost and surface the right shape, not to
produce production rulesets unattended.

## What pickled-spec does today

`RuleSetDrafter.draft_from_brief(brief_text, ruleset_short_name,
source_id, applies_to, active_from)` runs one LLM completion at
temperature 0 and returns `DraftResult(text, rationale, warnings)`.
The MCP surface is `rules_draft_ruleset_from_brief` with the same
arguments; the CLI surface is `pickled-rules draft`.

Validation runs after every completion. The emitted YAML is passed
through `load_ruleset_from_text`; if it raises
`RuleSetValidationError`, the message goes into `warnings` and the
raw text is returned anyway. A second validation pass checks the
emitted YAML against a forbidden-token list — `gdpr`, `hipaa`, `pci`,
`sox`, `iso27001`, `compliance`, `regulator`, `regulatory`, `legal`,
`law`, `lawful` — and for each occurrence emits a warning of the
shape `forbidden token '<token>' in YAML; rewrite the rule`. Neither
validation raises; the drafter never decides for the user that the
output is unusable, it just shows what it found.

The prompt template instructs the model to emit YAML matching the
canonical schema (metadata block plus rules list with id, title,
description, enforcement), then a literal `---RATIONALE---` line, then
one to three sentences explaining the rule selection. The drafter
splits on the sentinel; if the sentinel is missing, the entire output
becomes `text` and `rationale` is the empty string.

Model resolution, cache, and budget behave identically to every other
LLM-backed tool — all four flow through `build_default_client`.

## What we want to verify

Across the CLI and MCP surfaces:

- A well-formed brief plus valid metadata yields a `DraftResult`
  whose `text` parses cleanly through `load_ruleset_from_text` and
  whose `warnings` list is empty.
- A brief that pushes the model toward forbidden tokens (e.g. one
  that explicitly mentions a regulatory regime) yields a non-empty
  warnings list with one entry per forbidden token occurrence; the
  `text` is still returned for the user to remediate.
- A model emitting malformed YAML yields a warnings entry containing
  the parser's error message; the raw `text` is preserved verbatim
  so the user can see what the model produced.
- Output without the `---RATIONALE---` sentinel collapses cleanly:
  `rationale` becomes the empty string and `text` is the whole
  completion, no truncation.
- Identical inputs hit the disk cache and do not re-bill the
  provider. The cache key includes the metadata fields, not just
  the brief text — two briefs with the same text but different
  `source_id` produce separately cached entries.
- The metadata fields in the emitted YAML exactly equal the
  arguments passed in (`source_id`, `applies_to`, `active_from`);
  the model is never trusted to fill these from the brief.
- CLI exit codes: 0 with empty warnings, 1 with non-empty warnings,
  2 on a hard error (config missing, provider failure).

## Inventory references

- CLI: `pickled-rules draft --brief <PATH|-> --short-name <X>
  --source-id <Y> --applies-to <Z> --active-from <DATE>`
- MCP tools: `rules_draft_ruleset_from_brief`
- Gates: `RuleSetDrafter` (class in `pickled_rules.drafter`),
  `load_ruleset_from_text` (post-validation entry point)
- ADRs: ADR-0005 (LLM resolution), ADR-0006 (multi-ruleset)

## Open questions

- Forbidden-token list lives inline in the drafter today. As
  `pickled-rules` evolves and the canonical list of regulatory
  short-codes grows, this becomes a maintenance burden. Candidate:
  promote the list to a constant in `pickled_rules.constants` and
  cite it from both the drafter and the `rules-neutral-terminology`
  internal rule in `pickled-internal.yaml`.
- The drafter does not deduplicate rule IDs in its output. A model
  that emits two rules with the same `id` will produce a YAML that
  parses (the second silently shadows the first in many YAML
  libraries) but fails coverage downstream. Today this surfaces as
  a coverage gate failure, not a drafter warning — arguably a
  drafter-side validation gap.
- Rule descriptions in the emitted YAML are model-written and
  therefore drift from house style. There is no `--description-style`
  prompt knob yet. Tracked as a future enhancement under "house
  voice for rule descriptions".

## Status

draft
