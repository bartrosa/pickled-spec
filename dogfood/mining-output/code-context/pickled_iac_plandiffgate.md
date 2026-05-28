# Code context: PlanDiffGate.run

- **Surface id:** pickled_iac_plandiffgate
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 74 | **Truncated:** False

## Root: pickled_iac.gates.PlanDiffGate.run

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected head plan dict, got {type(target).__name__}",
            )
        base = ctx.get("base_plan")
        if not isinstance(base, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain "base_plan" dict',
            )

        head_changes = _index_changes(target)
        base_changes = _index_changes(base)
        findings: list[PlanDiffFinding] = []
        all_actions: set[str] = set()

        for address, actions in head_changes.items():
            all_actions.update(actions)
            if address not in base_changes:
                if actions:
                    findings.append(
                        PlanDiffFinding(address, (), tuple(actions)),
                    )
            elif base_changes[address] != actions:
                findings.append(
                    PlanDiffFinding(
                        address,
                        tuple(base_changes[address]),
                        tuple(actions),
                    ),
                )
                all_actions.update(actions)

        if not findings and not all_actions:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="No plan changes between base and head.",
            )

        if any(a in {"delete", "replace"} for a in all_actions):
            verdict = Verdict.FAIL
        elif all_actions <= {"create", "update", "read", "no-op"}:
            verdict = Verdict.WARN
        else:
            verdict = Verdict.WARN

        return GateResult(
            gate_name=self.name,
            verdict=verdict,
            findings=tuple(findings),
            notes=f"{len(findings)} resource change(s) detected.",
        )
```

## Callee: pickled_iac.gates._index_changes (hop 1)

```python
def _index_changes(plan: dict[str, Any]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for rc in plan.get("resource_changes", []) or []:
        if not isinstance(rc, dict):
            continue
        address = str(rc.get("address", ""))
        change = rc.get("change") or {}
        actions = change.get("actions") if isinstance(change, dict) else []
        if isinstance(actions, list):
            out[address] = [str(a) for a in actions]
    return out
```
