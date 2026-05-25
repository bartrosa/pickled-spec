"""LLM-driven analysis of plan diffs and security findings."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from pickled_core import LLMClient, PromptTemplate
from pickled_core.llm.turns import complete_prompt


def _prompt_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / name


@dataclass(frozen=True, slots=True)
class AdvisorResult:
    text: str
    warnings: tuple[str, ...] = ()


class IaCAdvisor:
    """Analyze plan diffs and security findings via the LLM."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._explain_tpl = PromptTemplate.from_file(_prompt_path("explain_plan_diff.md"))
        self._remediate_tpl = PromptTemplate.from_file(
            _prompt_path("suggest_security_remediation.md")
        )

    def explain_plan_diff(self, *, plan_json: str) -> AdvisorResult:
        warnings: list[str] = []
        try:
            json.loads(plan_json)
        except json.JSONDecodeError as exc:
            warnings.append(f"plan_json is not valid JSON: {exc}")
        prompt = self._explain_tpl.render(plan_json=plan_json)
        text = complete_prompt(
            self._llm,
            prompt,
            system="Output only the requested sections. No preamble.",
        ).strip()
        return AdvisorResult(text=text, warnings=tuple(warnings))

    def suggest_security_remediation(
        self,
        *,
        trivy_findings_json: str,
        hcl_text: str = "",
    ) -> AdvisorResult:
        warnings: list[str] = []
        try:
            findings = json.loads(trivy_findings_json)
            if not isinstance(findings, (list, dict)):
                warnings.append(
                    f"trivy_findings_json is JSON but not list/dict "
                    f"(got {type(findings).__name__})"
                )
        except json.JSONDecodeError as exc:
            warnings.append(f"trivy_findings_json is not valid JSON: {exc}")
        prompt = self._remediate_tpl.render(
            trivy_findings_json=trivy_findings_json,
            hcl_text=hcl_text,
        )
        text = complete_prompt(
            self._llm,
            prompt,
            system="Output only the requested sections. No preamble.",
        ).strip()
        return AdvisorResult(text=text, warnings=tuple(warnings))


__all__ = ["AdvisorResult", "IaCAdvisor"]
