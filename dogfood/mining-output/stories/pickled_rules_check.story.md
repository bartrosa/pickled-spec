# Story: check

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-rules
- **Surface id:** pickled_rules_check
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 1

## Context

This CLI command is invoked by users who want to verify that a Gherkin feature file (or set of feature files) satisfies a set of rules defined in a YAML ruleset. It reports coverage—whether required tags, scenario patterns, or other constraints defined in the ruleset are met by the feature file(s). The command is used in CI pipelines or local development to enforce behavioral documentation standards.

## What the target does today

**Input requirements:**
- Exactly one of `feature_path` or `feature_glob` must be provided; providing neither or both raises a ClickException.
- `ruleset` may be a built-in ruleset name (looked up from BUILTIN_RULESETS) or a file path; if a path is given and the file does not exist, raises ClickException.
- If `feature_glob` is provided, it is expanded using Python's glob module with recursive=True, and only files (not directories) matching the pattern are processed. If no files match, raises ClickException.
- If `feature_path` is provided, exactly one file is processed (the path itself).

**Ruleset resolution:**
- If `ruleset` is in BUILTIN_RULESETS, the built-in ruleset is loaded via resolve_ruleset_name.
- Otherwise, `ruleset` is treated as a file path and must exist.
- The ruleset is loaded via load_ruleset.
- The short name for the ruleset is determined by: `ruleset_name` (lowercased) if provided, else the `ruleset` argument (lowercased) if it's a built-in, else the file stem (lowercased).

**Feature parsing:**
- Feature files are parsed using PytestBddAdapter().parse_feature_file (delegated to unresolved collaborator; actual parsing behavior is opaque).
- Files are sorted before parsing.

**Coverage checking:**
- If exactly one feature file is processed, coverage_gate is called with the parsed feature, the ruleset, and the short name.
- If multiple feature files are processed, coverage_gate_features is called with the list of parsed features, the ruleset, and the short name. This performs union coverage (a rule is satisfied if any file in the set satisfies it).

**Reporting:**
- Output format is determined by `output_format` (case-insensitive):
  - "json" → render_coverage_json
  - Any other value → render_coverage_markdown
- The report includes the ruleset and the feature path(s). For single files, the path is the file path. For multiple files, the path label is a comma-separated list of sorted paths.
- If `quiet` is False and multiple files are processed, a message "Union coverage across N feature file(s)." is written to stderr.
- If `quiet` is True:
  - Only a verdict line "PASS: checked N feature(s)" or "FAIL: checked N feature(s)" is printed to stdout.
  - If `output` is provided, the full report is written to the file.
- If `quiet` is False:
  - If `output` is provided, the report is written to the file and a confirmation message "Report written to <path>" is written to stderr.
  - If `output` is not provided, the report is written to stdout.

**Exit behavior:**
- The gate result includes a Verdict. If the verdict is not Verdict.PASS, the process exits with status code 1.
- If the verdict is Verdict.PASS, the process exits with status code 0 (implicit).

**Side effects:**
- Writes to stderr when not quiet and when output file is written.
- Writes to stdout (report or verdict line) unless quiet with output file.
- Writes to the specified file if `output` is provided.
- Exits with status code 1 on coverage failure.

## What we want to verify

- Providing neither `feature_path` nor `feature_glob` raises ClickException with message "Provide --feature or --feature-glob".
- Providing both `feature_path` and `feature_glob` raises ClickException with message "Use only one of --feature or --feature-glob".
- Providing a `ruleset` path that does not exist raises ClickException with message "Rule set file not found: <path>".
- Providing a `feature_glob` that matches no files raises ClickException with message "No feature files matched".
- When `feature_glob` matches multiple files, only file paths (not directories) are processed.
- Feature files are processed in sorted order.
- When processing a single feature file, coverage_gate is called (not coverage_gate_features).
- When processing multiple feature files, coverage_gate_features is called and stderr receives a message about union coverage (unless quiet).
- When `output_format` is "json" (case-insensitive), the report uses render_coverage_json.
- When `output_format` is not "json", the report uses render_coverage_markdown.
- When `quiet` is True, stdout receives only "PASS: checked N feature(s)" or "FAIL: checked N feature(s)".
- When `quiet` is True and `output` is provided, the full report is written to the file.
- When `quiet` is False and `output` is provided, stderr receives "Report written to <path>".
- When `quiet` is False and `output` is None, stdout receives the full report.
- When the gate result verdict is not Verdict.PASS, the process exits with status code 1.
- When the gate result verdict is Verdict.PASS, the process exits with status code 0.
- When `ruleset` is a built-in name, the short name defaults to the built-in name (lowercased) if `ruleset_name` is not provided.
- When `ruleset` is a file path, the short name defaults to the file stem (lowercased) if `ruleset_name` is not provided.
- When `ruleset_name` is provided, it is used (lowercased) as the short name regardless of whether `ruleset` is built-in or a path.

## Inventory references

- Arguments:
- `ruleset` (required): Built-in rule set name or path to a YAML rule set file.
- `feature_path` (optional): Single Gherkin feature file to analyse.
- `feature_glob` (optional): Glob of feature files; multiple matches are checked as one union (strict rules must appear across the set, not in each file).
- `ruleset_name` (optional): Short name for tag prefix (default: built-in name or file stem).
- `output_format` (optional): Report output format.
- `output` (optional): Write the report to this path. Default: stdout.
- `quiet` (optional): Suppress report on stdout; print only the verdict line. If --output is set, the report is still written to the file.
- Related gates: coverage_gate, coverage_gate_features, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Check feature coverage against a YAML rule set" but does not mention that the command can fail with multiple specific error conditions (missing input, non-existent ruleset file, no matching feature files).
- Docstring drift: The docstring does not describe the command's exit behavior (exits with status 1 on coverage failure).
- Docstring drift: The docstring does not specify that the command can process multiple feature files via glob and that union coverage semantics apply in that case.
- Docstring drift: The docstring does not mention the quiet mode, output file, output format, or ruleset_name parameters and their effects on behavior.

## Status

draft
