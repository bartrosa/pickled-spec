# Story: draft

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-rules
- **Surface id:** pickled_rules_draft
- **Code depth:** callgraph | **Units read:** 8 | **Unresolved:** 3

## Context

This CLI command is invoked by end users (developers, compliance engineers) who want to automatically generate a YAML rule-set document from a natural-language description. The user provides a brief (either as a file path or via stdin), metadata fields (short_name, source_id, applies_to, active_from), and optionally an output file path. The command leverages an LLM client to transform the brief into structured YAML that conforms to the pickled-rules schema.

## What the target does today

The command accepts six parameters: a brief (file path or '-'), short_name, source_id, applies_to, active_from, and an optional output path. When brief is '-', the command reads from stdin; otherwise it reads UTF-8 text from the specified file path.

The command builds an LLM client using a factory specified by the PICKLED_RULES_LLM_FACTORY environment variable. If the LLM configuration is invalid, the command fails with a ClickException containing the configuration error message.

The command constructs a prompt incorporating the brief text and metadata fields, then delegates to an LLM completion call (unresolved; model, max_tokens, temperature, and stop parameters are supplied but exact LLM behavior is unobservable). The LLM response is expected to contain YAML text and optionally a rationale section separated by a sentinel string.

The command validates the generated YAML by attempting to load it as a rule set and checking for forbidden tokens in the lowercased YAML text. Validation warnings are collected but do not prevent output.

The command emits the generated YAML to the specified output file (UTF-8 encoded) or to stdout if output is None. Rationale lines (if present) are written to stderr prefixed with "rationale: ". Validation warnings (if any) are written to stderr prefixed with "warning: ".

The command exits with status 1 if any validation warnings are present, even though the YAML is still emitted. If an exception other than ClickException occurs during processing, the exception message is printed to stderr and the command exits with status 2.

## What we want to verify

- When brief is '-', the command reads from stdin; when brief is a file path, the command reads UTF-8 text from that file.
- When the LLM client cannot be built due to a configuration error, the command raises ClickException with the configuration error message.
- The command invokes the LLM client with a prompt containing the brief text, short_name, source_id, applies_to, and active_from values.
- The command attempts to validate the generated YAML by loading it as a rule set.
- The command checks the lowercased YAML text for forbidden tokens and produces warnings if any are found.
- When output is None, the generated YAML is written to stdout.
- When output is a Path, the generated YAML is written to that file with UTF-8 encoding.
- If the LLM response contains a rationale section (delimited by a sentinel), each rationale line is written to stderr prefixed with "rationale: ".
- Validation warnings are written to stderr prefixed with "warning: ".
- The command exits with status 1 if validation warnings are present, even if YAML was successfully emitted.
- The command exits with status 2 if a non-ClickException occurs, after printing the exception message to stderr.
- ClickExceptions are re-raised without being caught or transformed into SystemExit(2).

## Inventory references

- Arguments:
- `brief` (required): Brief file path or '-' for stdin.
- `short_name` (required): Ruleset short name for tagging.
- `source_id` (required): metadata.source_id value.
- `applies_to` (required): metadata.applies_to value.
- `active_from` (required): metadata.active_from (YYYY-MM-DD).
- `output` (optional): Write YAML to this path. Default: stdout.
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring claims the command "drafts a YAML rule set" but omits that validation warnings cause exit status 1 even when YAML is successfully generated and emitted.
- Docstring drift: The docstring does not mention that rationale output is written to stderr when present in the LLM response.
- Docstring drift: The docstring does not mention the command reads from stdin when brief is '-'.
- Docstring drift: The docstring does not mention the command validates the generated YAML for both schema conformance and forbidden tokens.
- Docstring drift: The docstring does not mention the two distinct failure modes: ClickException (configuration errors) versus general exceptions (exit status 2).

## Status

draft
