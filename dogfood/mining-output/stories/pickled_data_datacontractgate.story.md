# Story: DataContractGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-data
- **Surface id:** pickled_data_datacontractgate
- **Code depth:** callgraph | **Units read:** 4 | **Unresolved:** 2

## Context

DataContractGate.run is a gate implementation used to validate that SQL query column names match OpenAPI response property names. It is invoked within a gate-checking pipeline where SQL strings are verified against API schema definitions. The caller provides a SQL query string as the target and must supply an "endpoint_tag" in the context dictionary to identify which OpenAPI schema to validate against. This gate is part of a data contract validation system ensuring that database queries align with API contracts.

## What the target does today

**Input acceptance:**
- Accepts a `target` of any type and a `context` dictionary (optional, defaults to empty dict if None)
- Returns a FAIL verdict if `target` is not a string, with a note indicating the actual type received
- Returns a FAIL verdict if `context` does not contain an "endpoint_tag" key with a string value

**Schema resolution:**
- Returns a WARN verdict if no SchemaRegistry is configured on the gate instance (_registry is None)
- Delegates schema lookup to `_registry.find_schema_by_tag(endpoint_tag)` (unresolved call)
- Returns a WARN verdict if the schema artifact is not found for the given endpoint_tag

**Column extraction:**
- Extracts column names from the SQL string by parsing it as PostgreSQL dialect using sqlglot
- Handles parse failures silently, returning an empty list if parsing fails
- Collects column names from SELECT expressions, preferring aliases when present, falling back to the expression's name attribute
- Extracts OpenAPI response property names from the schema artifact's YAML content by:
  - Parsing YAML (returns empty list on parse error)
  - Navigating paths → [path] → [method] → responses → (200 or 201) → content → application/json → schema → properties
  - Returning sorted property names from the first matching operation found
- Returns a WARN verdict if no properties can be extracted from the OpenAPI schema

**Validation logic:**
- Compares SQL column names (as a set) against API property names (as a set)
- Computes missing columns (in SQL but not in API) and extra columns (in API but not in SQL)
- Returns a FAIL verdict if there are any missing or extra columns, with both lists sorted and included in notes
- Returns a PASS verdict only when column name sets match exactly

**Return value:**
- Always returns a GateResult object containing:
  - gate_name: the name of this gate instance
  - verdict: one of PASS, FAIL, or WARN
  - notes: a descriptive string explaining the verdict

**Explicitly not implemented:**
- Type checking of columns/properties (explicitly mentioned in PASS notes as "types not checked in v0.1")

## What we want to verify

- When target is not a string, verdict is FAIL with notes describing the actual type
- When context lacks "endpoint_tag" key or its value is not a string, verdict is FAIL
- When _registry is None, verdict is WARN with note "no SchemaRegistry configured"
- When schema artifact is not found for the given endpoint_tag, verdict is WARN with the tag name in notes
- When OpenAPI schema has no extractable properties, verdict is WARN
- When SQL parsing fails, the gate treats it as having zero columns and continues validation
- When SQL column set exactly matches API property set, verdict is PASS
- When SQL columns differ from API properties (missing or extra), verdict is FAIL with sorted lists of differences
- PASS verdict notes explicitly state that types are not checked in v0.1
- All GateResult objects include the gate's name and descriptive notes
- OpenAPI property extraction only examines 200 or 201 response codes
- OpenAPI property extraction returns names from the first matching operation found

## Inventory references

- Arguments:
- (gate class)
- Related gates: DataContractGate.run
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted
- ADR 0007: Code-aware stories and docstring drift detection — Accepted

## Open questions

- Docstring drift: Docstring claims "v0.1 PARTIAL: column name matching against OpenAPI response properties" but does not mention the multiple failure modes: non-string target rejection, missing endpoint_tag rejection, missing registry warning, missing schema warning, or unparseable OpenAPI warning
- Docstring drift: Docstring does not specify that the surface returns a GateResult object with verdict and notes fields
- Docstring drift: Docstring does not document the required context parameter structure (specifically that "endpoint_tag" must be present and be a string)

## Status

draft
