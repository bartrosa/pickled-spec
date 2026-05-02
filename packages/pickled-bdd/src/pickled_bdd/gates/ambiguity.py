"""Ambiguity gate — detects scenarios admitting multiple implementations."""

from __future__ import annotations

import json
from typing import Any

from pickled_core import (
    AmbiguityFinding,
    Feature,
    GateResult,
    LLMClient,
    PromptTemplate,
    Verdict,
)

from pickled_bdd.prompts import template_path


class AmbiguityGate:
    """Compensating gate: flags scenarios that admit multiple implementations.

    For each scenario, asks an LLM in adversarial-reviewer mode to
    enumerate alternative implementations. If the LLM finds genuine
    alternatives, the scenario is flagged.

    Verdict semantics:
    - **PASS:** no scenario is ambiguous (all evaluated scenarios are clear).
    - **WARN:** at least one scenario is ambiguous *or* some LLM responses
      could not be parsed (partial gate failure / local ambiguity).
    - **FAIL:** every scenario is ambiguous — treated as systemic confusion,
      not one-off wording issues.

    WARN vs FAIL distinguishes “fix a few scenarios” from “the whole feature
    is underspecified.”
    """

    name = "ambiguity"

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(template_path("ambiguity.md"))

    def run(
        self,
        target: object,
        *,
        context: dict[str, object] | None = None,
    ) -> GateResult:
        _ = context
        if not isinstance(target, Feature):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected Feature, got {type(target).__name__}",
            )

        findings: list[AmbiguityFinding] = []
        parse_errors: list[str] = []

        for scenario in target.scenarios:
            scenario_text = self._format_scenario(scenario.name, scenario.steps)
            prompt = self._template.render(scenario=scenario_text)
            response = self._llm.complete(
                prompt,
                system=(
                    "Reply with a single JSON object only. "
                    "No markdown fences, no commentary outside JSON."
                ),
            )
            parsed = self._parse_response(response)
            if parsed is None:
                parse_errors.append(scenario.name)
                continue
            if parsed.get("is_ambiguous"):
                alts_raw = parsed.get("alternatives", [])
                alts = tuple(str(x) for x in alts_raw) if isinstance(alts_raw, list) else ()
                findings.append(
                    AmbiguityFinding(
                        target_name=scenario.name,
                        alternatives=alts,
                        suggested_fix=str(parsed.get("suggested_fix", "")),
                    )
                )

        n = len(target.scenarios)
        if n > 0 and len(parse_errors) == n:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                findings=(),
                notes=f"Could not parse LLM response for: {parse_errors}",
            )

        ambiguous_count = len(findings)
        verdict = self._verdict(scenario_count=n, ambiguous_count=ambiguous_count)
        notes = f"{ambiguous_count}/{n} scenarios flagged ambiguous."
        if parse_errors:
            notes += f" Parse errors on: {parse_errors}."
        if parse_errors and verdict == Verdict.PASS:
            verdict = Verdict.WARN

        return GateResult(
            gate_name=self.name,
            verdict=verdict,
            findings=tuple(findings),
            notes=notes,
        )

    @staticmethod
    def _format_scenario(name: str, steps: tuple[str, ...]) -> str:
        lines = [f"Scenario: {name}"]
        lines.extend(f"  {step}" for step in steps)
        return "\n".join(lines)

    @staticmethod
    def _parse_response(response: str) -> dict[str, Any] | None:
        """Best-effort JSON extraction from the LLM response."""
        stripped = response.strip()
        if stripped.startswith("```"):
            parts = stripped.split("```")
            if len(parts) >= 2:
                block = parts[1]
                for prefix in ("json", "JSON"):
                    bl = block.lstrip()
                    if bl.startswith(prefix):
                        block = bl[len(prefix) :].lstrip()
                        break
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

    @staticmethod
    def _verdict(scenario_count: int, ambiguous_count: int) -> Verdict:
        if ambiguous_count == 0:
            return Verdict.PASS
        if scenario_count > 0 and ambiguous_count == scenario_count:
            return Verdict.FAIL
        return Verdict.WARN
