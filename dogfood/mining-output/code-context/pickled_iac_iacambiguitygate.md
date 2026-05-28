# Code context: IaCAmbiguityGate.run

- **Surface id:** pickled_iac_iacambiguitygate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 79 | **Truncated:** False

## Root: pickled_iac.gates.IaCAmbiguityGate.run

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, IaCArtifact):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected IaCArtifact, got {type(target).__name__}",
            )
        story = ctx.get("user_story")
        if not isinstance(story, str) or not story.strip():
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain non-empty "user_story"',
            )

        prompt = self._template.render(
            user_story=story,
            terraform_hcl=target.content,
        )
        from pickled_core.llm.turns import complete_prompt

        response = complete_prompt(
            self._llm,
            prompt,
            system="Reply with a single JSON object only. No markdown fences.",
        )
        parsed = _parse_json_object(response)
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
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.WARN,
            findings=tuple(ambiguities),
            notes=f"{len(ambiguities)} ambiguity(ies) reported.",
        )
```

## Callee: pickled_iac.gates._parse_json_object (hop 1)

```python
def _parse_json_object(response: str) -> dict[str, Any] | None:
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
    return data if isinstance(data, dict) else None
```

## Unresolved callees

- `self._template.render` — protocol or unknown attribute type
- `parts[1].lstrip()` — receiver is a subscript expression
- `block[4:].lstrip()` — receiver is a subscript expression
- `stripped.find` — variable 'stripped' reassigned; type not stable
- `stripped.rfind` — variable 'stripped' reassigned; type not stable
