# Story: iac_diff_terraform_plans

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-iac
- **Surface id:** iac_diff_terraform_plans

## Context

This MCP tool is called by automation workflows and CI/CD pipelines to analyze infrastructure changes between two Terraform plan states (base and head). Callers need to understand what resources will be added, modified, or destroyed when applying infrastructure-as-code changes, enabling them to validate changes before applying them to environments.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Accepts two required arguments: `base_plan_json` and `head_plan_json`
- Both arguments must be valid Terraform plan JSON format
- Returns a comparison result structure showing differences between the two plans
- Integrates with IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, and run_all gate operations
- Handles cases where base_plan_json represents the current state and head_plan_json represents proposed changes
- Produces output that can be consumed by the related gate implementations

## Inventory references

- Arguments:
- `base_plan_json` (required): 
- `head_plan_json` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

(none)

## Status

draft
