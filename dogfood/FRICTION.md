# Dogfood friction log

Observations from semi-automatic dogfood loops. Each session appends a section.

## Session 2026-05-25 — bdd-drafter

- pickled-bdd CLI has no `ambiguity` subcommand (real: `check --gate ambiguity`)
- workspace runner hardcodes `features/` path, forces symlink hack when workspace organizes by package subdirs
- AmbiguityGate FAIL 13/13 on bdd-drafter feature — need to inspect findings to determine if gate is over-restrictive or drafter is over-disjunctive
- coverage gaps across 6 rulesets are expected and form roadmap for remaining 8 stories
