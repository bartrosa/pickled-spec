# Story: check

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_check
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 2

## Context

This is a CLI command that runs quality gates on BDD feature files. The caller (a user at the command line or test automation) wants to validate a Gherkin feature file for ambiguity issues and receive a JSON report with an exit code indicating the verdict. The command is intended to be part of a CI/CD pipeline or pre-commit workflow where feature file quality must be enforced.

## What the target does today

Accepts two parameters: a `feature_file` string (path to a .feature file) and a `gate` string parameter. The `gate` parameter is currently unused; regardless of its value, only the ambiguity gate is executed.

Builds an LLM client by delegating to an external factory. If the factory environment variable `PICKLED_BDD_LLM_FACTORY` is set, that factory is used; otherwise a default client is built. If client construction fails due to a configuration error, raises a `click.ClickException` with the error message.

Parses the feature file using an unresolved `PytestBddAdapter().parse_feature_file()` call. The parsing behavior is not observable from this surface.

If the LLM client is None (null), returns a gate result with verdict PASS, gate name "ambiguity", and a note explaining the LLM was unavailable and the gate was skipped. Otherwise, delegates gate execution to an unresolved `AmbiguityGate(llm).run(feature)` call.

Transforms the gate result into JSON with the following structure:
- `gate`: the gate name string
- `verdict`: the verdict enum value as a string
- `notes`: notes string from the result
- `findings`: an array of objects, each containing `scenario` (target name), `alternatives` (list), and `suggested_fix`, filtered to only include findings that are instances of `AmbiguityFinding`

Outputs the JSON to stdout via `click.echo` with 2-space indentation and Unicode preservation (ensure_ascii=False).

Terminates the process with an exit code derived from the verdict:
- Verdict.PASS → exit code 0
- Verdict.WARN → exit code 1
- Verdict.FAIL → exit code 2

## What we want to verify

- When invoked with a valid feature file path, the command parses the file and produces JSON output to stdout
- The JSON output contains exactly four top-level keys: "gate", "verdict", "notes", and "findings"
- The "gate" value in JSON output is "ambiguity"
- When the LLM client is unavailable (None), verdict is "PASS" and notes indicate the gate was skipped
- When the LLM client is unavailable, the findings array is empty
- The process exits with code 0 when verdict is PASS
- The process exits with code 1 when verdict is WARN
- The process exits with code 2 when verdict is FAIL
- When LLM client construction fails with ConfigError, a ClickException is raised with the original error message
- The `gate` parameter value has no effect on which gate runs; ambiguity gate always executes
- JSON output uses 2-space indentation
- JSON output preserves Unicode characters (non-ASCII characters are not escaped)
- The findings array only includes items that are instances of AmbiguityFinding
- Each finding object contains "scenario", "alternatives" (as a list), and "suggested_fix" keys

## Inventory references

- Arguments:
- `feature_file` (required): 
- `gate` (optional): Which gate to run.
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Run compensating gates against a .feature file" (plural "gates") but the code only runs the ambiguity gate, ignoring the `gate` parameter entirely
- Docstring drift: The docstring describes the surface as running "compensating gates" but provides no explanation of what "compensating" means or why this terminology is used; the code implements quality validation gates with no observable compensating behavior

## Status

draft
