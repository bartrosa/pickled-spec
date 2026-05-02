# Architecture Decision Records

This directory holds ADRs for pickled-spec. ADRs are short, dated
documents capturing significant architectural decisions and the
reasoning behind them.

## How to add an ADR

1. Copy `0000-template.md` to a new file with the next number prefix
   and a kebab-case slug: `0001-second-package.md`.
2. Fill in Context, Decision, Consequences, Alternatives.
3. Open a PR. Discussion happens in the PR; the ADR is committed once
   the decision is made.
4. Once accepted, edit the ADR's Status to "Accepted" and merge.

## When to write one

Write an ADR for any decision that:

- Affects the public API of `pickled-core` or any package.
- Changes the architectural pattern (oracle classification, gate
  taxonomy).
- Picks one tool/library over another for cross-cutting infrastructure
  (uv vs. hatch, anthropic vs. another LLM client default, etc.).

Don't write an ADR for routine implementation choices, refactors, or
test-only changes.

## Index

- (none yet — first real ADR will be 0001-second-package.md, recording
  the v0.2 choice between pickled-schema and pickled-policy.)
