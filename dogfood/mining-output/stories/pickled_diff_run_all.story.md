# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-diff
- **Surface id:** pickled_diff_run_all
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 0

## Context

This gate function is the main entry point for the pickled-diff differential testing framework. It is invoked by the pickled gate runner to verify that a candidate implementation matches an oracle implementation across a corpus of test inputs. Users configure the gate through a `pickled.diff.yaml` configuration file in their project, specifying oracle and candidate commands, a corpus file, an optional comparator, and optional timeout settings.

## What the target does today

**Signature**: Accepts a single parameter `workdir` (Path or str) representing the working directory root, and returns a list of `GateResult` objects.

**Configuration discovery**: Searches for a configuration file named `pickled.diff.yaml` in the working directory. If not found, returns a single-element list containing a `GateResult` with gate_name "diff.config", verdict WARN, and a note about the missing configuration file.

**Configuration parsing and validation**: If a configuration file is found, attempts to parse it as YAML and extract:
- `oracle_command`: command-line arguments for the oracle subprocess (validated to be a list)
- `candidate_command`: command-line arguments for the candidate subprocess (validated to be a list)
- `corpus`: a path string to a corpus file (must be a string, otherwise raises ValueError)
- `comparator`: optional string naming the comparator strategy (defaults to "exact")
- `timeout_seconds`: optional numeric timeout value (defaults to 30)

**Error handling for configuration**: If configuration parsing fails due to ValueError, FileNotFoundError, json.JSONDecodeError, or TypeError, returns a single-element list containing a `GateResult` with gate_name "diff.config", verdict FAIL, and the exception message as notes.

**Python executable normalization**: When the oracle or candidate command starts with "python" or "python3" (and has additional arguments), replaces that first token with `sys.executable` to ensure the current Python interpreter is used.

**Corpus loading**: Loads the corpus from the specified path relative to the working directory root. The corpus loading mechanism is delegated to an unresolved `_load_corpus` function.

**Command resolution**: Resolves command arguments using `_resolve_argv` and `_argv_list`, which handle path resolution relative to the working directory root.

**Comparator selection**: Selects a comparator function by name via an unresolved `_comparator` function.

**Differential oracle execution**: Creates a `DifferentialOracleGate` with two `SubprocessRunner` instances (oracle and candidate), each configured with:
- Resolved command arguments
- A name identifier ("oracle" or "candidate")
- The configured timeout
- The working directory as `cwd`

Runs the differential gate on the loaded corpus and returns a single-element list containing a `GateResult` with gate_name "diff.differential_oracle", copying the verdict, findings, and notes from the gate's result.

**Return value**: Always returns a list of `GateResult` objects. The list contains exactly one element in all code paths: either a configuration-related result (WARN or FAIL) or a differential oracle execution result.

## What we want to verify

- When `pickled.diff.yaml` is absent, returns a list with one GateResult having gate_name "diff.config", verdict WARN, and notes mentioning the missing file
- When configuration file exists but corpus key is not a string, returns a list with one GateResult having gate_name "diff.config" and verdict FAIL
- When configuration file exists but oracle_command or candidate_command are not lists, returns a list with one GateResult having gate_name "diff.config" and verdict FAIL
- When configuration is valid, returns a list with one GateResult having gate_name "diff.differential_oracle"
- When oracle_command starts with "python" or "python3", the subprocess runner uses sys.executable instead
- When candidate_command starts with "python" or "python3", the subprocess runner uses sys.executable instead
- Python executable substitution only occurs when the command has more than one element
- Configuration timeout_seconds defaults to 30 when not specified
- Configuration comparator defaults to "exact" when not specified
- FileNotFoundError during configuration loading results in verdict FAIL, not WARN
- JSONDecodeError during corpus loading results in verdict FAIL with the exception message in notes
- The returned list always contains exactly one GateResult object

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

- Docstring drift: The docstring states the gate runs "when `pickled.diff.yaml` is present" but the code actually runs (and returns a result) even when the file is absent—it returns a WARN verdict in that case rather than skipping execution
- Docstring drift: The docstring does not mention searching for `diff/pickled.diff.yaml` as an alternative location, but the notes field in the WARN result explicitly mentions "diff/pickled.diff.yaml" as a possible location
- Docstring drift: The docstring does not describe the return type (list of GateResult objects) or any of the failure modes (configuration errors, missing corpus, invalid commands)

## Status

draft
