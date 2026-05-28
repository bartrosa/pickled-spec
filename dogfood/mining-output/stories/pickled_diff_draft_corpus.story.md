# Story: draft-corpus

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-diff
- **Surface id:** pickled_diff_draft_corpus

## Context

Developers and test engineers use `draft-corpus` to generate larger differential test corpora from a small set of seed examples. This is typically needed when creating test datasets that require many variations of similar items, where manually writing each example would be tedious. The command takes seed data and expands it to a specified target size, optionally incorporating additional notes.

## What the target does today

The `draft-corpus` command expands seed examples into a larger differential corpus. It reads seed items from a JSON file (or stdin when '-' is specified), generates additional corpus items to reach the specified target size, and outputs the resulting corpus as JSON. An optional notes file can be provided to influence corpus generation. By default, output is written to stdout, but can be directed to a file via the `--output` option.

## What we want to verify

- When given a seeds JSON file and target_size, the command produces a corpus with exactly target_size items
- When seeds is '-', the command reads seed data from stdin
- When output is not specified, the command writes the corpus JSON to stdout
- When output is specified, the command writes the corpus JSON to the specified file path
- When notes is '-', the command reads notes from stdin
- When notes is a file path, the command reads notes from that file
- The output is valid JSON
- The output corpus includes the original seed items or variations derived from them
- When target_size is less than or equal to the number of seeds, the command handles this appropriately
- The command exits with status 0 on successful corpus generation

## Inventory references

- Arguments:
- `seeds` (required): JSON file with seed items, or '-' for stdin.
- `target_size` (required): Total corpus size.
- `notes` (optional): Optional notes file path or '-' for stdin.
- `output` (optional): Write corpus JSON to this path. Default: stdout.
- Related gates: run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

(none)

## Status

draft
