# Story: run_all

## Metadata

- **Surface kind:** gate
- **Package:** pickled-iac
- **Surface id:** pickled_iac_run_all
- **Code depth:** callgraph | **Units read:** 6 | **Unresolved:** 0

## Context

This is a top-level gate orchestrator for Infrastructure-as-Code (IaC) validation in the pickled-iac package. It is invoked by a CI/CD pipeline or quality gate system to verify Terraform or OpenTofu configurations before deployment. The function expects to be called with a project root directory and returns a list of gate results covering both structural validation and security baseline checks. It is designed to fail gracefully when tools are missing, treating missing dependencies as warnings rather than hard failures where appropriate.

## What the target does today

Accepts a single argument `workdir` (Path or str) representing the project root directory and returns a list of GateResult objects.

**Directory structure requirements:**
- Resolves `workdir` to an absolute path and checks for an `infra/` subdirectory
- If `infra/` does not exist, returns a single-element list containing a GateResult with gate_name="iac.infra", verdict=WARN, and notes="no infra/ directory"
- If `infra/` exists, proceeds with validation and security checks

**Terraform/OpenTofu validation (iac.validate gate):**
- Attempts to run `terraform validate -json` (or OpenTofu equivalent) on the `infra/` directory
- If the IaC binary (terraform/tofu) is not found on PATH, returns a GateResult with verdict=WARN and notes containing the IaCToolMissingError message
- If the binary is found but initialization or validation fails with an unexpected exception, returns a GateResult with verdict=FAIL and notes containing the exception message
- On successful validation execution, returns a GateResult with:
  - verdict=PASS if the validation reports valid=true
  - verdict=FAIL if the validation reports valid=false
  - notes containing semicolon-separated diagnostic messages, or "ok" if no diagnostics are present

**Terraform initialization:**
- Automatically initializes the Terraform directory (runs `terraform init -input=false -backend=false`) if `.terraform/` does not exist
- Uses environment variable TF_IN_AUTOMATION=1 for all subprocess calls
- Raises RuntimeError if initialization fails

**Security baseline scan (delegated to SecurityBaselineGate):**
- Always attempts a Trivy security scan via SecurityBaselineGate().run(infra)
- If `trivy` is not found on PATH, returns a GateResult with verdict=PASS and notes="trivy not found on PATH — security scan skipped"
- If `trivy` is found, runs `trivy config <infra> --format json --severity HIGH,CRITICAL --quiet`
- On trivy execution errors (non-0/1 return codes with no stdout), returns verdict=WARN with error details
- On JSON parse errors, returns verdict=WARN with notes="trivy returned non-JSON output"
- On successful scan:
  - verdict=FAIL with findings tuple of CRITICAL titles if any CRITICAL severity misconfigurations are found
  - verdict=WARN with findings tuple of HIGH titles if any HIGH severity misconfigurations are found (and no CRITICAL)
  - verdict=PASS with notes="No HIGH or CRITICAL findings." if no HIGH or CRITICAL findings exist

**Return value structure:**
- Always returns a list of GateResult objects
- When `infra/` is missing: returns 1 result
- When `infra/` exists: returns 2 results (iac.validate + security baseline)
- Each GateResult includes gate_name, verdict, and notes; security results may also include findings tuple

## What we want to verify

- When workdir contains no infra/ subdirectory, returns a single GateResult with verdict=WARN and gate_name="iac.infra"
- When infra/ exists and terraform/tofu is not on PATH, iac.validate result has verdict=WARN with IaCToolMissingError message in notes
- When infra/ exists and terraform validate succeeds with valid=true, iac.validate result has verdict=PASS
- When infra/ exists and terraform validate succeeds with valid=false, iac.validate result has verdict=FAIL and diagnostics in notes
- When terraform validate raises an unexpected exception, iac.validate result has verdict=FAIL with exception message in notes
- When trivy is not found on PATH, security baseline result has verdict=PASS with skip message in notes
- When trivy finds CRITICAL severity misconfigurations, security baseline result has verdict=FAIL with findings tuple
- When trivy finds HIGH severity misconfigurations (no CRITICAL), security baseline result has verdict=WARN with findings tuple
- When trivy finds no HIGH or CRITICAL misconfigurations, security baseline result has verdict=PASS
- When trivy returns non-JSON output, security baseline result has verdict=WARN
- Return value is always a list, never None or a single GateResult
- All terraform/tofu subprocess calls include TF_IN_AUTOMATION=1 environment variable
- If .terraform/ does not exist in infra/, terraform init is executed before validate

## Inventory references

- Arguments:
- (gate class)
- Related gates: run_all
- Related ADRs:
- (none directly relevant)

## Open questions

- Docstring drift: Docstring claims the function performs "``terraform validate``" but does not mention that it auto-detects and supports OpenTofu (tofu) as an alternative binary
- Docstring drift: Docstring states "optional Trivy scan" but the code always attempts the security scan; it is only skipped when trivy is not found on PATH, not based on any configuration option or parameter
- Docstring drift: Docstring does not mention the function returns different result counts (1 vs 2 GateResult objects) depending on whether infra/ exists
- Docstring drift: Docstring does not describe the warning behavior when infra/ is missing, terraform/tofu is missing, or trivy is missing
- Docstring drift: Docstring does not mention automatic terraform initialization when .terraform/ directory is absent

## Status

draft
