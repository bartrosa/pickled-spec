# Story: diff_verify_against_oracle

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-diff
- **Surface id:** diff_verify_against_oracle

## Context

This tool is used by testers, CI pipelines, or developers who need to verify that a candidate implementation produces the same output as a reference (oracle) implementation across a corpus of test inputs. It automates regression testing and behavioral comparison between two commands by running both against multiple test items and reporting differences.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Tool accepts `oracle_command` parameter (required) for the reference command
- Tool accepts `candidate_command` parameter (required) for the command under test
- Tool accepts `corpus_items` parameter (required) for the set of inputs to test
- Tool accepts optional `comparator` parameter to customize difference detection
- Tool accepts optional `timeout_seconds` parameter to limit execution time per command
- Tool executes both oracle and candidate commands against each item in the corpus
- Tool reports differences between oracle and candidate outputs
- Related gate `run_all` exists in the target package

## Inventory references

- Arguments:
- `oracle_command` (required): 
- `candidate_command` (required): 
- `corpus_items` (required): 
- `comparator` (optional): 
- `timeout_seconds` (optional): 
- Related gates: run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

(none)

## Status

draft
