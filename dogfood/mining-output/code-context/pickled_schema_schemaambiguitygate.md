# Code context: SchemaAmbiguityGate.run

- **Surface id:** pickled_schema_schemaambiguitygate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 88 | **Truncated:** False

## Root: pickled_schema.gates.SchemaAmbiguityGate.run

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, SchemaArtifact):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected SchemaArtifact, got {type(target).__name__}",
            )
        gherkin = ctx.get("gherkin_context")
        if not isinstance(gherkin, str) or not gherkin.strip():
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain non-empty "gherkin_context"',
            )

        prompt = self._template.render(
            gherkin_context=gherkin,
            schema_yaml=target.content,
        )
        from pickled_core.llm.turns import complete_prompt

        response = complete_prompt(
            self._llm,
            prompt,
            system=(
                "Reply with a single JSON object only. "
                "No markdown fences, no commentary outside JSON."
            ),
        )
        parsed = _parse_ambiguity_response(response)
        if parsed is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes="LLM returned malformed JSON",
            )

        ambiguities = parsed.get("ambiguities", [])
        if not isinstance(ambiguities, list):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='LLM JSON missing list field "ambiguities"',
            )

        if not ambiguities:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="No ambiguities reported.",
            )

        notes = f"{len(ambiguities)} ambiguity(ies) reported."
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.WARN,
            findings=tuple(ambiguities),
            notes=notes,
        )
```

## Callee: pickled_schema.gates._parse_ambiguity_response (hop 1)

```python
def _parse_ambiguity_response(response: str) -> dict[str, Any] | None:
    stripped = response.strip()
    if stripped.startswith("```"):
        parts = stripped.split("```")
        if len(parts) >= 2:
            block = parts[1].lstrip()
            if block.lower().startswith("json"):
                block = block[4:].lstrip()
            stripped = block.strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    return data
```

## Unresolved callees

- `self._template.render` — protocol or unknown attribute type
- `parts[1].lstrip()` — receiver is a subscript expression
- `block[4:].lstrip()` — receiver is a subscript expression
- `stripped.find` — variable 'stripped' reassigned; type not stable
- `stripped.rfind` — variable 'stripped' reassigned; type not stable
