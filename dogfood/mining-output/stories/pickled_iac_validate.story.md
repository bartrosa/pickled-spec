# Story: validate

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-iac
- **Surface id:** pickled_iac_validate

## Context

CLI users invoke this command to run Terraform's built-in validate operation on a specified directory containing Terraform configuration files. This is typically used as part of a validation pipeline or gate system (as evidenced by related gates like IaCAmbiguityGate, PlanDiffGate, and SecurityBaselineGate) to ensure Terraform configurations are syntactically valid and internally consistent before planning or applying changes.

## What the target does today

Run terraform validate on a directory.

The command accepts a required `tf_dir` parameter specifying the target directory and executes Terraform's validate command against that directory.

## What we want to verify

- Invoking `validate` with a valid `tf_dir` argument executes terraform validate on the specified directory
- The command accepts `tf_dir` as a required parameter
- The command fails or reports an error when `tf_dir` is not provided
- The command passes validation results (success or failure) back to the caller
- The command operates on the directory specified by `tf_dir` rather than the current working directory

## Inventory references

- Arguments:
- `tf_dir` (required): 
- Related gates: IaCAmbiguityGate.run, PlanDiffGate.run, SecurityBaselineGate.run, run_all
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
