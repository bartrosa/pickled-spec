# Story: SchemaCoverageGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-schema
- **Surface id:** pickled_schema_schemacoveragegate
- **Code depth:** callgraph | **Units read:** 3 | **Unresolved:** 2

## Context

This surface is a gate implementation used in the pickled-schema package to validate that endpoint references in Gherkin feature files (marked with `@schema:endpoint:*` tags) actually exist in a corresponding OpenAPI specification. It is invoked by a gate runner that passes an OpenAPI spec dictionary as the target and provides feature file paths or text content via the context dictionary. This gate is part of a quality/validation workflow to ensure API test scenarios reference valid API endpoints.

## What the target does today

**Inputs:**
- `target`: Expected to be a dictionary representing a parsed OpenAPI specification. If not a dict, the gate fails immediately.
- `context`: Optional dictionary that may contain:
  - `"feature_paths"`: A list of file paths (convertible to `Path` objects) pointing to feature files
  - `"feature_texts"`: A list of strings, each containing feature file text content

**Returns:**
A `GateResult` object with fields:
- `gate_name`: Set to `self.name`
- `verdict`: One of `Verdict.PASS` or `Verdict.FAIL`
- `notes`: Human-readable description of the result
- `findings`: A tuple of `SchemaCoverageFinding` objects (only present on certain failure modes)

**Validation & Failure Modes:**

1. **Type validation**: If `target` is not a dictionary, returns FAIL with notes indicating the actual type received.

2. **Context validation**: If the context dictionary contains neither `"feature_paths"` nor `"feature_texts"` (or both are absent/empty after type filtering), returns FAIL with notes stating the requirement for these keys.

3. **Schema coverage check**: 
   - Extracts endpoint tags from feature file content using a pattern matching mechanism (delegated to `_ENDPOINT_TAG_RE.finditer`)
   - Each tag is parsed to extract an HTTP method and path
   - For each tag, checks whether the OpenAPI spec contains a matching endpoint by:
     - Looking up the path in `spec["paths"]` dictionary
     - Verifying the path entry is a dictionary
     - Checking if the lowercased HTTP method exists as a key in that path's dictionary
   - Returns FAIL if any tags reference endpoints not found in the spec, with `findings` containing `SchemaCoverageFinding` objects (each with `tag` and `source` attributes) and notes listing each missing endpoint as "{tag} ({source})" separated by semicolons
   - Returns PASS if all tags have matching endpoints, with notes "All @schema:endpoint tags have matching paths."

**Context Processing:**
- `feature_paths`: Only list items are processed; each is converted to a `Path` object. Files are read with UTF-8 encoding.
- `feature_texts`: Only string items within the list are processed; each is paired with a synthetic source identifier `"<feature-{i}>"` where `i` is the list index.
- Non-conforming items in these lists are silently ignored.

**Side Effects:**
- Reads files from disk for each path in `feature_paths`
- No other observable side effects

## What we want to verify

- When target is not a dict (e.g., string, None, list), returns GateResult with verdict=FAIL and notes describing the type mismatch
- When context is None or missing both "feature_paths" and "feature_texts" keys, returns GateResult with verdict=FAIL and notes requiring these context keys
- When context contains empty lists for both "feature_paths" and "feature_texts", returns GateResult with verdict=FAIL
- When feature files contain endpoint tags and all referenced endpoints exist in the OpenAPI spec's paths with matching HTTP methods, returns GateResult with verdict=PASS
- When at least one endpoint tag references a path not present in spec["paths"], returns GateResult with verdict=FAIL and findings containing the missing tag
- When an endpoint tag references a path that exists but the HTTP method is not defined for that path, returns GateResult with verdict=FAIL and findings containing the missing tag
- When spec["paths"] is missing or not a dict, endpoint lookups fail and return GateResult with verdict=FAIL for any tags found
- HTTP method matching is case-insensitive (methods are lowercased before lookup)
- Feature files specified in "feature_paths" are read with UTF-8 encoding
- When "feature_texts" contains non-string items, they are silently skipped
- When "feature_paths" contains non-path-convertible items, they are silently skipped (based on isinstance check)
- Multiple missing endpoints are accumulated and reported together in the notes as semicolon-separated list
- findings tuple contains SchemaCoverageFinding objects with tag and source attributes identifying each missing endpoint
- Source identifier for feature_texts items is "<feature-{index}>" where index is the position in the list
- Source identifier for feature_paths items is the string representation of the file path

## Inventory references

- Arguments:
- (gate class)
- Related gates: SchemaCoverageGate.run
- Related ADRs:
- ADR 0004: Multi-ruleset workspace configuration — Accepted

## Open questions

- Docstring drift: The docstring states the surface verifies "@schema:endpoint:* tags" but the actual pattern matching mechanism and tag format are delegated to an unresolved regex pattern (`_ENDPOINT_TAG_RE`), so the exact tag syntax cannot be confirmed from the visible code
- Docstring drift: The docstring does not mention the specific context dictionary keys ("feature_paths" and "feature_texts") required for operation, though this is a critical input requirement
- Docstring drift: The docstring does not describe the return type (GateResult) or the failure modes (type validation, missing context, missing endpoints)
- Docstring drift: The docstring does not mention that HTTP method matching is case-insensitive

## Status

draft
