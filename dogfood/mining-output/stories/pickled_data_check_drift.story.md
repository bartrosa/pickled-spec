# Story: check-drift

## Metadata

- **Surface kind:** cli_command
- **Package:** pickled-data
- **Surface id:** pickled_data_check_drift

## Context

This surface is used by developers and CI/CD pipelines to validate that a migration script produces a database schema that matches an expected schema defined in a YAML file. It runs the MigrationDriftGate to detect discrepancies between what the migration creates and what was documented as expected. This is particularly relevant in the context of ADR 0007, which establishes code-aware stories and docstring drift detection as a practice.

## What the target does today

The command runs MigrationDriftGate against an expected schema YAML file. It accepts:
- A required `migration` parameter (the migration to verify)
- A required `expected` parameter (the expected schema YAML to compare against)
- An optional `dialect` parameter (presumably to specify database dialect)

The gate checks whether the migration, when executed, produces a schema that matches the expected schema definition. This helps detect drift between documented schema expectations and actual migration behavior.

## What we want to verify

- Accepts a required `migration` argument that specifies which migration to validate
- Accepts a required `expected` argument that points to a schema YAML file
- Accepts an optional `dialect` argument for database dialect specification
- Executes MigrationDriftGate.run with the provided parameters
- Reports drift or validation results from comparing migration output to expected schema
- Exits with appropriate status code indicating success or drift detection
- Can be invoked from command line as part of the pickled-data CLI

## Inventory references

- Arguments:
- `migration` (required): 
- `expected` (required): 
- `dialect` (optional): 
- Related gates: DataContractGate.run, MigrationDriftGate.run, run_all
- Related ADRs:
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

(none)

## Status

draft
