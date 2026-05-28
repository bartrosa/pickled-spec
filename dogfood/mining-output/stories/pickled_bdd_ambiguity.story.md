# Story: ambiguity

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-bdd
- **Surface id:** pickled_bdd_ambiguity
- **Code depth:** callgraph | **Units read:** 5 | **Unresolved:** 2

## Context

This CLI command provides a shortcut for running the ambiguity gate on a Gherkin feature file. It is invoked directly by users via the command line as an alternative to the more verbose `pickled-bdd check --gate ambiguity` syntax. The command parses the feature file, evaluates it for ambiguous scenarios using an LLM, and reports findings as JSON output with an exit code reflecting the gate verdict.

## What the target does today

**Inputs:**
- `feature_file` (str, required): Path to a Gherkin feature file to be analyzed.

**Execution:**
1. Writes an informational message to stderr indicating equivalence to `pickled-bdd check --gate ambiguity`.
2. Builds an LLM client via environment-based configuration. If the `PICKLED_BDD_LLM_FACTORY` environment variable is set, uses that factory; otherwise uses a default client builder from `pickled_core.llm.bootstrap`.
3. Parses the feature file using an unresolved `PytestBddAdapter().parse_feature_file()` call.
4. If LLM client construction succeeds, runs an unresolved `AmbiguityGate(llm).run(feature)` call to evaluate the feature.
5. If LLM is unavailable (None), returns a PASS verdict with notes "LLM unavailable; ambiguity gate skipped" without performing analysis.
6. Outputs a JSON object to stdout containing:
   - `"gate"`: the string `"ambiguity"`
   - `"verdict"`: one of `"PASS"`, `"WARN"`, or `"FAIL"` (string value from the Verdict enum)
   - `"notes"`: a string (may be empty or contain explanatory text)
   - `"findings"`: an array of objects, each with:
     - `"scenario"`: string name of the scenario
     - `"alternatives"`: list of alternative interpretations
     - `"suggested_fix"`: suggested resolution text
   - Only findings that are instances of `AmbiguityFinding` are included.
7. Exits the process with status code determined by verdict: 0 for PASS, 1 for WARN, 2 for FAIL.

**Error conditions:**
- If LLM client configuration fails (e.g., invalid environment configuration), raises `click.ClickException` with the original `ConfigError` message.
- If feature file parsing fails, behavior is determined by the unresolved `PytestBddAdapter().parse_feature_file()` call.
- If the ambiguity gate evaluation fails, behavior is determined by the unresolved `AmbiguityGate(llm).run()` call.

**Side effects:**
- Writes informational message to stderr.
- Writes JSON output to stdout.
- Exits the process with a non-zero code for WARN or FAIL verdicts.

## What we want to verify

- Accepts a single required `feature_file` string argument.
- Writes the message "(equivalent to: pickled-bdd check --gate ambiguity)" to stderr before performing analysis.
- When LLM configuration is invalid, raises `click.ClickException` with the configuration error message.
- When LLM is unavailable (None), outputs JSON with verdict "PASS" and notes "LLM unavailable; ambiguity gate skipped".
- Outputs valid JSON to stdout with keys: "gate", "verdict", "notes", and "findings".
- The "gate" field in JSON output always has value "ambiguity".
- The "verdict" field contains one of the string values: "PASS", "WARN", or "FAIL".
- The "findings" array contains only objects with "scenario", "alternatives", and "suggested_fix" keys.
- Exits with code 0 when verdict is PASS.
- Exits with code 1 when verdict is WARN.
- Exits with code 2 when verdict is FAIL.
- JSON output is formatted with 2-space indentation and non-ASCII characters are preserved (ensure_ascii=False).

## Inventory references

- Arguments:
- `feature_file` (required): 
- Related gates: AmbiguityGate.run, run_all
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

- Docstring drift: The docstring describes this as an "alias" but the implementation is a standalone function that duplicates logic rather than directly calling the `check --gate ambiguity` code path. The function writes a message claiming equivalence but executes independent ambiguity gate logic via `run_ambiguity_gate()`.

## Status

draft
