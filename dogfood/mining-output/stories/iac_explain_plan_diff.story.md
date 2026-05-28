# Story: iac_explain_plan_diff

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-iac
- **Surface id:** iac_explain_plan_diff

## Context

This tool is used by infrastructure-as-code workflows that need to understand the impact and risk of Terraform plan changes. Callers provide a Terraform plan JSON file and receive a summary highlighting potentially dangerous operations. This enables automated review gates, pre-deployment risk assessment, and human-readable explanations of infrastructure changes before they are applied.

## What the target does today

The tool accepts a Terraform plan JSON file as input and produces a summary that identifies risky actions within the plan. Based on the related gates (IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate), the tool likely evaluates the plan against multiple risk dimensions including ambiguous configurations, plan differences, and security baseline violations, then flags actions that meet risk criteria.

## What we want to verify

- Accepts valid Terraform plan JSON as the `plan_json` parameter
- Returns a summary output (format to be confirmed from implementation)
- Identifies and flags risky actions within the provided plan
- Invokes or integrates with IaCAmbiguityGate.run to detect ambiguous infrastructure configurations
- Invokes or integrates with PlanDiffGate.run to analyze plan differences
- Invokes or integrates with SecurityBaselineGate.run to check security policy violations
- Processes the plan_json parameter as required (non-optional)
- Handles malformed or invalid Terraform plan JSON appropriately (error behavior TBD)
- The summary distinguishes between different types of risk categories flagged by the gates
- Integration with run_all suggests batch or orchestrated gate execution

## Inventory references

- Arguments:
- `plan_json` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
