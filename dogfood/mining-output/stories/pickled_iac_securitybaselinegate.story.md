# Story: SecurityBaselineGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-iac
- **Surface id:** pickled_iac_securitybaselinegate
- **Code depth:** callgraph | **Units read:** 1 | **Unresolved:** 0

## Context

This gate is part of a quality-assurance pipeline for Infrastructure-as-Code (Terraform) configurations. Callers invoke `run` to verify that Terraform code meets security baseline requirements by scanning for HIGH and CRITICAL severity misconfigurations. It is designed to be optional (can gracefully degrade) and integrates with the Trivy security scanner.

## What the target does today

**Accepts:**
- `target`: an object that must be a `Path` instance pointing to a Terraform directory
- `context`: an optional dictionary (accepted but ignored)

**Returns:**
A `GateResult` object with fields `gate_name`, `verdict`, and optionally `findings` and `notes`. The verdict is one of `PASS`, `WARN`, or `FAIL`.

**Rejection and error modes:**
1. If `target` is not a `Path` instance, returns `FAIL` verdict with a note describing the type mismatch.
2. If the `trivy` executable is not found on the system PATH, returns `PASS` verdict with a note explaining the scan was skipped (graceful degradation).
3. If `trivy` exits with a return code other than 0 or 1 and produces no stdout, returns `WARN` verdict with stderr captured in the notes.
4. If `trivy` output is not valid JSON, returns `WARN` verdict with a note about non-JSON output.

**Security scan behavior:**
- Invokes the external `trivy` command-line tool with arguments: `config <target_path> --format json --severity HIGH,CRITICAL --quiet`
- Parses the JSON output looking for a top-level `"Results"` array, then within each result a `"Misconfigurations"` array
- Extracts severity (`"Severity"` field, case-insensitive comparison) and title (`"Title"` field, falling back to `"ID"` or the string `"finding"`)
- Classifies findings as CRITICAL or HIGH based on severity

**Verdict logic:**
- Returns `FAIL` if any CRITICAL findings are detected; the `findings` tuple contains all CRITICAL titles, and notes report the count.
- Returns `WARN` if no CRITICAL findings but one or more HIGH findings are detected; the `findings` tuple contains all HIGH titles, and notes report the count.
- Returns `PASS` if no HIGH or CRITICAL findings are detected, with a note confirming this.

**Side effects:**
- Executes an external subprocess (`trivy`), which may perform network requests (e.g., to download vulnerability databases) or file I/O depending on Trivy's configuration.
- Captures stdout and stderr from the subprocess; does not stream or log them separately.

## What we want to verify

- When `target` is not a `Path`, returns `GateResult` with `verdict=FAIL` and notes containing the actual type name.
- When `trivy` executable is not on PATH, returns `GateResult` with `verdict=PASS` and notes indicating scan was skipped.
- When `trivy` exits with return code other than 0 or 1 and produces empty stdout, returns `GateResult` with `verdict=WARN` and notes containing stderr content.
- When `trivy` output is not valid JSON, returns `GateResult` with `verdict=WARN` and notes about non-JSON output.
- When `trivy` reports one or more CRITICAL misconfigurations, returns `GateResult` with `verdict=FAIL`, `findings` containing titles, and notes reporting count.
- When `trivy` reports HIGH but no CRITICAL misconfigurations, returns `GateResult` with `verdict=WARN`, `findings` containing titles, and notes reporting count.
- When `trivy` reports no HIGH or CRITICAL misconfigurations, returns `GateResult` with `verdict=PASS` and notes confirming no findings.
- The `context` parameter is accepted but does not influence the result.
- `trivy` is invoked with arguments `config`, target path as string, `--format json`, `--severity HIGH,CRITICAL`, and `--quiet`.
- Non-dict entries in `"Results"` or `"Misconfigurations"` arrays are silently skipped.
- Severity strings are compared case-insensitively (uppercased).
- Title extraction falls back from `"Title"` to `"ID"` to the literal string `"finding"`.

## Inventory references

- Arguments:
- (gate class)
- Related gates: SecurityBaselineGate.run
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: The docstring states the scan is "optional in v0.1" but does not clarify that the gate passes automatically (not skips with a different status) when `trivy` is absent. The code reveals this graceful-degradation behavior: missing `trivy` yields `PASS`, not an error or a skip state.
- Docstring drift: The docstring describes the surface as "Run Trivy config scan" but omits all information about return values, verdict logic (FAIL for CRITICAL, WARN for HIGH, PASS otherwise), error handling (malformed JSON, subprocess errors), and input validation (type check on `target`).

## Status

draft
