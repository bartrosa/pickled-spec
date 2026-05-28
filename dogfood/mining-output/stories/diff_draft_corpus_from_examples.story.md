# Story: diff_draft_corpus_from_examples

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-diff
- **Surface id:** diff_draft_corpus_from_examples

## Context

This tool is used by developers or automated systems working with the pickled-diff package to generate draft corpora for differential testing. It takes a small set of seed examples and expands them to a target size, allowing users to create larger test datasets from a representative sample. The optional notes parameter enables documentation of the corpus generation process.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Accepts `seed_examples` as a required parameter
- Accepts `target_size` as a required parameter indicating desired corpus size
- Accepts optional `notes` parameter for additional context or documentation
- Produces a draft corpus output (format to be verified from source)
- Expands the provided seed examples to reach the specified target size (mechanism to be verified)
- Returns a result that can be consumed by or integrated with the `run_all` gate

## Inventory references

- Arguments:
- `seed_examples` (required): 
- `target_size` (required): 
- `notes` (optional): 
- Related gates: run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

(none)

## Status

draft
