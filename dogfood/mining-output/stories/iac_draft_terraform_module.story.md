# Story: iac_draft_terraform_module

## Metadata

- **Surface kind:** mcp_tool
- **Package:** pickled-iac
- **Surface id:** iac_draft_terraform_module

## Context

Infrastructure-as-code engineers and automation workflows use this tool to generate Terraform module drafts from natural-language user stories. The surface sits behind the MCP (Model Context Protocol) tool interface and is part of the pickled-iac package's module generation pipeline. Callers expect to provide a user story description and optionally specify a cloud provider, receiving in return a drafted Terraform module that can then pass through related gates (IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate) for validation.

## What the target does today

The inventory provides no docstring for this surface; behavior must be confirmed from source before specifying.

## What we want to verify

- Call with a minimal user story string and verify a response is returned
- Call with `user_story` parameter populated and `provider` parameter omitted; confirm default provider handling or appropriate error
- Call with both `user_story` and `provider` parameters populated; verify provider-specific module generation
- Call with missing required `user_story` parameter; verify error or rejection
- Verify output format conforms to Terraform module structure expectations
- Confirm generated module can be consumed by related gates (IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run)
- Call with edge-case user stories (empty string, extremely long text, special characters); verify graceful handling
- Verify interaction with run_all gate when this tool's output is part of a multi-gate workflow

## Inventory references

- Arguments:
- `user_story` (required): 
- `provider` (optional): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- ADR 0001: pickled-diff package — Proposed

## Open questions

(none)

## Status

draft
