# Story: plan-cmd

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_plan_cmd

## Context

This CLI command is used by infrastructure engineers and DevOps practitioners to execute Terraform plan operations and capture the resulting plan output in JSON format. The command is part of the pickled-iac package's workflow for analyzing infrastructure-as-code changes before applying them. Users invoke this command to generate structured plan data that can then be fed into various gates (IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate) for validation and safety checks.

## What the target does today

Run terraform plan and write JSON to *output*.

The command accepts two required parameters: a Terraform directory path (`tf_dir`) where the Terraform configuration resides, and an output path (`output`) where the JSON-formatted plan results will be written.

## What we want to verify

- Command accepts `tf_dir` argument specifying a directory containing Terraform configuration files
- Command accepts `output` argument specifying a file path for the resulting JSON
- Command executes `terraform plan` in the specified `tf_dir` directory
- Command captures the Terraform plan output in JSON format
- Command writes the JSON-formatted plan data to the file path specified by `output`
- Command creates the output file if it does not exist
- Command exits with appropriate status code reflecting success or failure of the terraform plan operation
- Generated JSON output is valid and parseable JSON
- Generated JSON output can be consumed by related gates (IaCAmbiguityGate, PlanDiffGate, SecurityBaselineGate)

## Inventory references

- Arguments:
- `tf_dir` (required): 
- `output` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- (none directly relevant)

## Open questions

(none)

## Status

draft
