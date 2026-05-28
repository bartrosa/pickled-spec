# Story: SchemaAmbiguityGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-schema
- **Surface id:** pickled_schema_schemaambiguitygate
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 5

## Context

This gate is used within a staged schema validation pipeline to perform an LLM-driven ambiguity check on a drafted SchemaArtifact. The caller (typically a gate runner or pipeline orchestrator) provides a SchemaArtifact target and context containing Gherkin specification text. The gate uses an LLM to identify ambiguities, inconsistencies, or unclear mappings between the Gherkin context and the schema YAML content.

## What the target does today

**Inputs:**
- `target`: Expected to be a SchemaArtifact instance; any other type causes immediate failure.
- `context`: Optional dictionary; must contain a key `"gherkin_context"` with a non-empty string value. If `context` is None or missing this key, or the value is not a non-empty string, the gate fails.

**Processing:**
1. Validates that `target` is a SchemaArtifact. If not, returns a FAIL verdict with a note indicating the received type.
2. Validates that `context` contains `"gherkin_context"` as a non-empty string. If missing, empty, or not a string, returns a FAIL verdict with a descriptive note.
3. Renders a prompt using an internal template (unresolved call) with the Gherkin context and the schema YAML content from the target.
4. Sends the prompt to an LLM via an unresolved `complete_prompt` call with a system instruction requiring a single JSON object response without markdown fences or extra commentary.
5. Parses the LLM response as JSON:
   - Strips leading/trailing whitespace.
   - If the response starts with triple-backtick markdown fences (with optional "json" label), extracts the content between the fences.
   - Attempts to parse the extracted or original stripped response as JSON.
   - If JSON parsing fails at any stage, returns None from the parser.
6. If parsing returns None (malformed JSON), the gate returns FAIL with note "LLM returned malformed JSON".
7. Extracts the `"ambiguities"` field from the parsed JSON:
   - If the field is missing or not a list, returns FAIL with note 'LLM JSON missing list field "ambiguities"'.
   - If the list is empty, returns PASS with note "No ambiguities reported."
   - If the list is non-empty, returns WARN with the count of ambiguities in the notes and the list items as findings.

**Return value:**
Always returns a `GateResult` with:
- `gate_name`: the gate's name
- `verdict`: one of FAIL, PASS, or WARN
- `notes`: descriptive string explaining the outcome
- `findings`: tuple of ambiguity items (only present for WARN verdict when ambiguities are reported)

**Failure modes:**
- Target is not a SchemaArtifact → FAIL
- Context missing or `gherkin_context` absent/empty/non-string → FAIL
- LLM response not parseable as JSON (with or without markdown fences) → FAIL
- Parsed JSON lacks `"ambiguities"` as a list → FAIL
- Empty ambiguities list → PASS (not a failure)
- Non-empty ambiguities list → WARN (not a failure, but flagged for review)

**Side effects:**
Calls an unresolved LLM completion function, which may incur API usage, rate limiting, or other external effects.

## What we want to verify

- Gate returns FAIL verdict with type mismatch note when target is not a SchemaArtifact instance
- Gate returns FAIL verdict when context is None and requires gherkin_context
- Gate returns FAIL verdict when context dict lacks "gherkin_context" key
- Gate returns FAIL verdict when "gherkin_context" is an empty string or whitespace-only string
- Gate returns FAIL verdict when "gherkin_context" is not a string type
- Gate returns FAIL verdict with "LLM returned malformed JSON" note when LLM response is not valid JSON
- Gate returns FAIL verdict with "LLM returned malformed JSON" note when LLM response has unmatched or malformed markdown fences
- Gate returns FAIL verdict when parsed JSON does not contain "ambiguities" key
- Gate returns FAIL verdict when "ambiguities" value is not a list type
- Gate returns PASS verdict with "No ambiguities reported." note when "ambiguities" is an empty list
- Gate returns WARN verdict with count in notes when "ambiguities" list contains one or more items
- Gate attaches ambiguities list items as findings tuple in GateResult when verdict is WARN
- Gate passes rendered prompt with gherkin_context and schema YAML content to LLM completion
- Gate instructs LLM via system message to return only JSON without markdown fences or commentary
- Gate successfully parses LLM response when wrapped in triple-backtick fences with optional "json" label
- Gate successfully parses LLM response when returned as plain JSON without fences

## Inventory references

- Arguments:
- (gate class)
- Related gates: SchemaAmbiguityGate.run
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

- Docstring drift: Docstring describes the gate as a "Second LLM critic pass" but does not mention it is specifically focused on ambiguity detection between Gherkin context and schema content.
- Docstring drift: Docstring does not describe the required context structure (must contain "gherkin_context" key with non-empty string).
- Docstring drift: Docstring does not describe the three possible verdict outcomes (FAIL, PASS, WARN) or the conditions under which each occurs.
- Docstring drift: Docstring does not describe the findings field populated when ambiguities are detected.
- Docstring drift: Docstring does not describe the multiple specific failure modes (wrong target type, missing context, malformed LLM JSON, missing ambiguities field).

## Status

draft
