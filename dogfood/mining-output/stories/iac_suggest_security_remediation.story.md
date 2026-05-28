# Story: iac_suggest_security_remediation

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-iac
- **Surface id:** iac_suggest_security_remediation

## Context

This surface is used by security and infrastructure engineers who have run Trivy configuration scans against Infrastructure-as-Code files and need actionable remediation advice. The tool bridges the gap between security findings (JSON output from Trivy) and concrete HCL code patches, allowing teams to fix misconfigurations without manually researching each vulnerability.

## What the target does today

The surface accepts Trivy configuration scan findings in JSON format and suggests HCL (HashiCorp Configuration Language) patches to remediate the identified security issues. An optional HCL text parameter allows the tool to provide context-aware suggestions specific to existing code. The tool generates patch recommendations that address the security findings reported by Trivy.

## What we want to verify

- The surface accepts valid Trivy config-scan JSON output as the `trivy_findings_json` parameter
- The surface returns suggested HCL patches corresponding to the security findings provided
- When `hcl_text` is provided, the suggestions reference or are tailored to the supplied HCL context
- When `hcl_text` is omitted, the surface still produces generic remediation patches based solely on the Trivy findings
- The surface handles Trivy JSON containing zero findings without error
- The surface handles Trivy JSON containing multiple findings and produces suggestions for each
- The output format is suitable for applying patches to HCL configuration files
- The surface validates that `trivy_findings_json` conforms to expected Trivy output schema before processing

## Inventory references

- Arguments:
- `trivy_findings_json` (required): 
- `hcl_text` (optional): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
