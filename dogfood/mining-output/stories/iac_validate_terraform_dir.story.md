# Story: iac_validate_terraform_dir

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-iac
- **Surface id:** iac_validate_terraform_dir

## Context

This tool is used by AI agents or automation workflows that need to validate Terraform infrastructure-as-code files before applying them. The caller has written Terraform configuration files to a temporary directory and wants to verify the syntax and structure are valid before proceeding with planning or deployment. This surface is part of the pickled-iac package's MCP tool interface, making it accessible to agents that consume MCP-compatible tools.

## What the target does today

Validate Terraform files written to a temp directory.

The surface accepts a required `tf_files` parameter and performs validation on Terraform configuration files in a temporary directory location. The validation likely checks syntax correctness and structural validity of the Terraform code. Related gates (IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate) suggest this validation may be part of a broader quality and security checking pipeline.

## What we want to verify

- When invoked with valid Terraform files in `tf_files`, the surface returns a success result
- When invoked with syntactically invalid Terraform files, the surface returns an error or validation failure
- The surface accepts the `tf_files` parameter as required input
- The surface can process multiple Terraform files in a single invocation
- Validation results distinguish between syntax errors and valid configurations
- The surface operates on files in a temporary directory context

## Inventory references

- Arguments:
- `tf_files` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
