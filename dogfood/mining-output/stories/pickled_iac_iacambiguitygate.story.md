# Story: IaCAmbiguityGate.run

## Metadata

- **Surface kind:** gate
- **Package:** pickled-iac
- **Surface id:** pickled_iac_iacambiguitygate
- **Code depth:** callgraph | **Units read:** 2 | **Unresolved:** 5

## Context

This surface is a quality gate that evaluates Infrastructure-as-Code (Terraform) artifacts against a user story to detect ambiguities. It is used within a pipeline or workflow where Terraform modules are validated against business requirements. The caller provides an IaCArtifact containing Terraform HCL and a context dictionary with a user story, expecting a GateResult that indicates whether the implementation has potential ambiguities that need attention.

## What the target does today

The surface accepts three parameters: `target` (an object), and an optional `context` keyword parameter (a dictionary mapping strings to any type or None).

**Type validation:**
The surface requires `target` to be an instance of `IaCArtifact`. If not, it returns a FAIL verdict with a note indicating the actual type received.

The surface requires `context` (or an empty dict if None) to contain a "user_story" key whose value is a non-empty string (after stripping whitespace). If missing, not a string, or empty after stripping, it returns a FAIL verdict with a note stating the requirement.

**LLM interaction:**
When validation passes, the surface renders a template (delegated to `self._template.render`) using the user story and the `content` attribute of the target artifact. It then sends the rendered prompt to an LLM via `complete_prompt` from `pickled_core.llm.turns`, requesting JSON-only output with no markdown fences.

**Response parsing:**
The surface attempts to parse the LLM response as a JSON object. The parsing logic:
- Strips whitespace from the response
- If the response starts with "```", it attempts to extract content between the first and last "```" delimiters
- Extracts the substring between the first `{` and last `}` characters (inclusive)
- Parses this substring as JSON

If JSON parsing fails or produces a non-dictionary, the surface returns FAIL with note "LLM returned malformed JSON".

If the parsed JSON lacks an "ambiguities" key or its value is not a list, the surface returns FAIL with note 'LLM JSON missing list field "ambiguities"'.

**Verdict determination:**
- If the "ambiguities" list is empty, returns PASS with note "No ambiguities reported."
- If the "ambiguities" list is non-empty, returns WARN verdict with the list converted to a tuple in the `findings` field and a note indicating the count of ambiguities

All returned GateResult objects include `gate_name` set to `self.name`.

## What we want to verify

- Surface returns FAIL verdict when target is not an IaCArtifact instance
- Surface returns FAIL verdict when context is None and default dict has no "user_story" key
- Surface returns FAIL verdict when context["user_story"] is not a string
- Surface returns FAIL verdict when context["user_story"] is an empty or whitespace-only string
- Surface renders template with user_story and target.content attributes
- Surface calls complete_prompt with system message requesting JSON without markdown
- Surface returns FAIL verdict when LLM response cannot be parsed as JSON
- Surface returns FAIL verdict when parsed JSON is not a dictionary
- Surface returns FAIL verdict when parsed JSON lacks "ambiguities" key
- Surface returns FAIL verdict when "ambiguities" value is not a list
- Surface returns PASS verdict when "ambiguities" list is empty
- Surface returns WARN verdict when "ambiguities" list contains one or more items
- Surface includes findings as tuple when verdict is WARN
- Surface includes gate name in all returned GateResult objects
- Surface handles LLM response wrapped in markdown code fences (starting with "```")
- Surface extracts JSON between first '{' and last '}' after stripping/unwrapping

## Inventory references

- Arguments:
- (gate class)
- Related gates: IaCAmbiguityGate.run
- Related ADRs:
- ADR 0005: `pickled-spec mine` staged mining pipeline — Accepted

## Open questions

- Docstring drift: Docstring describes surface as "LLM critic for Terraform modules" but does not mention the requirement for a "user_story" in the context parameter, which is a mandatory input that causes FAIL if absent
- Docstring drift: Docstring does not mention the return type (GateResult) or the possible verdict values (PASS, WARN, FAIL)
- Docstring drift: Docstring does not mention that the surface specifically checks for "ambiguities" in the LLM response
- Docstring drift: Docstring does not describe the validation requirements for the target parameter (must be IaCArtifact)

## Status

draft
