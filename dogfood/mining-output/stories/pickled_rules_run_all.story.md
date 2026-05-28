# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-rules
- **Surface id:** pickled_rules_run_all
- **Code depth:** callgraph | **Units read:** 7 | **Unresolved:** 2

## Context

This gate is used by continuous integration or quality assurance processes to verify that BDD feature files reference a required set of rules defined in YAML ruleset files. It ensures that all "strict" enforcement rules are covered by at least one feature scenario tag, enforcing traceability between requirements/regulations and test scenarios. The caller invokes this with a working directory containing both feature files and a `pickled.ruleset.yaml` configuration file.

## What the target does today

**Inputs:**
- `workdir`: a filesystem path (string or Path object) to a directory containing BDD feature files and a `pickled.ruleset.yaml` configuration

**Returns:**
A list of `GateResult` objects, where each result corresponds to one ruleset's coverage evaluation. The list is never empty—at minimum one result is returned.

**Configuration Loading:**
The surface reads `pickled.ruleset.yaml` from the working directory root. If the file is missing or empty, the gate returns a single WARN result with the note "missing pickled.ruleset.yaml or ruleset/rulesets key". If the file contains invalid YAML or is not a dictionary, it is treated as an empty configuration.

**Ruleset Configuration:**
The configuration file supports two mutually exclusive keys:
- `ruleset`: a string path to a single ruleset file, with optional `ruleset_short_name` to specify its identifier (defaults to the file stem)
- `rulesets`: a list of mappings, each with required `path` (string) and optional `short_name` (string, defaults to the path stem)

If both keys are present, the gate returns a single FAIL result with notes explaining the mutual exclusivity violation. If `rulesets` is present but empty, or if any list item is malformed (non-dict, missing/non-string path, non-string short_name), the gate returns a single FAIL result with a descriptive validation message. Duplicate short names across rulesets entries result in a FAIL with position information.

**Feature File Discovery:**
The gate uses the `feature_glob` configuration key (defaults to `"features/**/*.feature"`) to discover feature files via glob pattern matching. If `feature_glob` is present but not a string, the gate raises `RuleSetValidationError`. If no feature files match the pattern, the gate returns a single WARN result with the note "no feature files".

**Feature Parsing:**
All discovered feature files are parsed using `PytestBddAdapter().parse_feature_file()`, which is an unresolved call. The parsing behavior and error handling is delegated to that collaborator.

**Per-Ruleset Evaluation:**
For each configured ruleset entry:
1. The gate name is `"rules.coverage"` if only one ruleset exists, otherwise `"rules.coverage.{short_name}"`
2. If the ruleset file does not exist, a FAIL result is returned with notes indicating the missing file path
3. The ruleset YAML is loaded and validated; if loading fails due to malformed content, a FAIL result with gate name `"rules.load.{short_name}"` is returned with the validation error message
4. Coverage is computed by extracting scenario tag references from all parsed features and matching them against the ruleset rules
5. A FAIL verdict is issued if any strict-enforcement rules are unreferenced OR if any unknown rule references are found in the features
6. A PASS verdict is issued only when all strict rules are referenced and no unknown references exist
7. The result includes traces linking each referenced rule to the feature artifact with relation "implements" and confidence "asserted"

**Side Effects:**
- Reads files from the filesystem: `pickled.ruleset.yaml`, ruleset YAML files, and feature files
- Resolves all paths relative to the working directory root

**Error Handling:**
Validation errors during configuration or ruleset loading are captured and returned as FAIL results within the list rather than being raised as exceptions. The only exception is if `feature_glob` is invalid, which raises `RuleSetValidationError`.

## What we want to verify

- When `pickled.ruleset.yaml` is missing, returns a single WARN result with gate_name "rules.coverage" and notes about missing configuration
- When `pickled.ruleset.yaml` contains both "ruleset" and "rulesets" keys, returns a single FAIL result describing mutual exclusivity
- When "ruleset" key contains a non-string value, returns a single FAIL result with validation message
- When "rulesets" key contains a non-list value, returns a single FAIL result with validation message
- When "rulesets" list is empty, returns a single FAIL result requiring at least one entry
- When "rulesets" contains entries with duplicate short_name values, returns a single FAIL result identifying the duplicate positions
- When no feature files match the configured glob pattern, returns a single WARN result with notes "no feature files"
- When a single ruleset is configured, the returned result uses gate_name "rules.coverage"
- When multiple rulesets are configured, each result uses gate_name "rules.coverage.{short_name}"
- When a configured ruleset file does not exist, returns a FAIL result with notes indicating the missing path
- When a ruleset file contains invalid YAML, returns a FAIL result with gate_name "rules.load.{short_name}" and the validation error
- When all strict rules are referenced and no unknown references exist, returns a PASS verdict
- When any strict-enforcement rule is unreferenced, returns a FAIL verdict with count in notes
- When scenario tags reference unknown rule IDs, returns a FAIL verdict with count in notes
- PASS results include traces for each referenced rule with relation "implements" and artifact_kind "feature"
- The surface always returns a non-empty list of GateResult objects

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states "Run coverage gate for each feature" but the gate actually runs for each *ruleset* and evaluates coverage across *all* features collectively per ruleset, not per individual feature
- Docstring drift: The docstring does not mention the WARN verdict cases (missing configuration, no features)
- Docstring drift: The docstring does not mention the special handling for ruleset loading failures that produce "rules.load.{short_name}" gate names
- Docstring drift: The docstring does not describe the configuration schema or the mutual exclusivity of "ruleset" vs "rulesets" keys

## Status

draft
