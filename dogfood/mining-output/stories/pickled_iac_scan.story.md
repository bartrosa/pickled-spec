# Story: scan

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_scan
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 0

## Context

A CLI command surface that performs security scanning on Terraform configuration directories. Called by operators or CI/CD pipelines to validate infrastructure-as-code against security baselines. The command runs Trivy config scanning, returns structured JSON output to stdout, and uses exit codes to signal pass/fail status. Designed to fail builds when critical security issues are found while allowing graceful degradation when the scanner tool is unavailable.

## What the target does today

**Acceptance:**
- Accepts a single positional argument `tf_dir` typed as `Path` representing a Terraform configuration directory
- Does not validate that `tf_dir` exists, is a directory, or contains Terraform files before passing to the security gate

**Returns and output:**
- Always writes a JSON object to stdout (via `click.echo`) with three fields:
  - `verdict`: string representation of the scan result ("PASS", "WARN", or "FAIL")
  - `notes`: human-readable explanation of the verdict
  - `findings`: list of finding titles (populated only when issues are detected)
- The JSON is formatted with 2-space indentation

**Exit behavior:**
- Exits with code 2 (via `SystemExit(2)`) when verdict is `FAIL`
- Exits with code 0 (implicit) when verdict is `PASS` or `WARN`

**Security scanning logic:**
- If `trivy` executable is not found on PATH: returns `PASS` verdict with note "trivy not found on PATH — security scan skipped"
- If `tf_dir` is not a Path instance: returns `FAIL` verdict with type mismatch note
- When Trivy is available, invokes: `trivy config <target> --format json --severity HIGH,CRITICAL --quiet`
- If Trivy exits with code other than 0 or 1 AND produces no stdout: returns `WARN` verdict with stderr content
- If Trivy output is not valid JSON: returns `WARN` verdict with note "trivy returned non-JSON output"
- Parses Trivy JSON report looking for `Results[].Misconfigurations[]` entries
- Extracts `Severity` and `Title` (falling back to `ID` or "finding") from each misconfiguration
- If any CRITICAL severity findings exist: returns `FAIL` verdict with findings list and count
- If any HIGH severity findings exist (and no CRITICAL): returns `WARN` verdict with findings list and count
- If no HIGH or CRITICAL findings: returns `PASS` verdict

**Error handling:**
- Non-zero Trivy exit codes are tolerated; only codes other than 0 or 1 combined with empty stdout trigger warnings
- JSON decode errors are caught and converted to `WARN` verdicts
- Non-dict entries in Results or Misconfigurations arrays are silently skipped
- Missing or null nested structures are handled gracefully with `or []` guards

## What we want to verify

- When `trivy` is not on PATH, output verdict is "PASS" and notes indicate scan was skipped, exit code is 0
- When `tf_dir` is not a Path instance, output verdict is "FAIL" and notes mention type mismatch, exit code is 2
- When Trivy is available and finds no HIGH/CRITICAL issues, output verdict is "PASS", findings list is empty, exit code is 0
- When Trivy reports CRITICAL findings, output verdict is "FAIL", findings list contains CRITICAL issue titles, exit code is 2
- When Trivy reports only HIGH findings (no CRITICAL), output verdict is "WARN", findings list contains HIGH issue titles, exit code is 0
- When Trivy returns non-JSON output, output verdict is "WARN" and notes indicate non-JSON output, exit code is 0
- When Trivy fails with non-0/1 exit code and empty stdout, output verdict is "WARN" and notes contain stderr content, exit code is 0
- Output is always valid JSON with exactly three keys: verdict, notes, findings
- Findings list only contains titles/IDs from HIGH or CRITICAL severity misconfigurations
- Exit code is 2 if and only if verdict is "FAIL"

## Inventory references

- Arguments:
- `tf_dir` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: Docstring says "optional; skips if trivy missing" but does not document that the command returns structured JSON output to stdout
- Docstring drift: Docstring does not mention that the command exits with code 2 on security failures (FAIL verdict)
- Docstring drift: Docstring does not indicate that WARN verdicts (HIGH findings) allow the command to exit successfully (code 0)
- Docstring drift: Docstring omits that invalid input types are rejected with FAIL verdict
- Docstring drift: Docstring does not document the severity filtering behavior (HIGH and CRITICAL only)
- Docstring drift: Docstring describes it as a "config scan" which aligns with the implementation, but omits that it specifically targets security misconfigurations

## Status

draft
