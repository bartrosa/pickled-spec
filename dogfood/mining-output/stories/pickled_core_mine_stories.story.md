# Story: mine stories

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-core
- **Surface id:** pickled_core_mine_stories

## Context

Developers and CI pipelines use `mine stories` during the third stage of a three-stage mining workflow. After `mine inventory` has collected surface metadata and `mine code-context` has extracted implementation details, this command generates human-readable story files that document the behavior of each mined surface. The stories serve as both documentation and the foundation for feature-file generation in stage 4.

## What the target does today

Stage 3: emit stories from inventory.json.

The command reads the inventory file produced by stage 1 and generates story documentation for each surface. It accepts filtering by package name or surface-id substring via the `surfaces` parameter. The `quick` flag controls whether the command runs in batch mode (default) or prompts interactively. Parallel LLM calls can be limited with `max_parallel` for stories and features generation. The `overwrite_stories` flag controls whether existing story files should be replaced. If a `code_context_dir` is provided or defaults to `<output>/code-context`, the command can incorporate implementation details into the generated stories (per ADR 0007). The `verbose` flag enables additional diagnostic output to stderr.

## What we want to verify

- Reads inventory.json from the target directory
- Generates story files in the output directory structure
- Filters surfaces when `surfaces` parameter contains package name or surface-id substring
- Defaults to quick/batch mode unless `quick` is explicitly disabled
- Respects `max_parallel` limit for concurrent LLM operations
- Honors `overwrite_stories` flag for existing story file handling
- Looks for code-context files in `code_context_dir` if specified, otherwise defaults to `<output>/code-context`
- Emits extra logging to stderr when `verbose` is enabled
- Integrates code-context into stories when available, supporting drift detection per ADR 0007

## Inventory references

- Arguments:
- `target` (required): 
- `output_dir` (optional): Mining output directory.
- `quick` (optional): Quick mode (default) or interactive prompts.
- `verbose` (optional): Extra logging to stderr.
- `surfaces` (optional): Comma-separated filter on package name or surface-id substring.
- `max_parallel` (optional): Max parallel LLM calls in quick mode (stories, features).
- `overwrite_stories` (optional): 
- `code_context_dir` (optional): Directory with code-context/*.md (default: <output>/code-context when present).
- Related gates: (none)
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
