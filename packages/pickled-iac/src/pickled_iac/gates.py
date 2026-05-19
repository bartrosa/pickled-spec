"""Compensating gates for pickled-iac."""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pickled_core import GateResult, LLMClient, PromptTemplate, Verdict

from pickled_iac.types import IaCArtifact


def _prompt_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / name


@dataclass(frozen=True, slots=True)
class PlanDiffFinding:
    address: str
    actions_before: tuple[str, ...]
    actions_after: tuple[str, ...]


class IaCAmbiguityGate:
    """LLM critic for Terraform modules."""

    name = "iac_ambiguity"

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(_prompt_path("ambiguity.md"))

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


class PlanDiffGate:
    """Compare two terraform plan JSON outputs (base vs head)."""

    name = "iac_plan_diff"

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


class SecurityBaselineGate:
    """Run Trivy config scan on a Terraform directory (optional in v0.1)."""

    name = "iac_security_baseline"

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        _ = context
        if not isinstance(target, Path):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected Path to tf dir, got {type(target).__name__}",
            )
        trivy = shutil.which("trivy")
        if trivy is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="trivy not found on PATH — security scan skipped",
            )

        proc = subprocess.run(
            [
                trivy,
                "config",
                str(target),
                "--format",
                "json",
                "--severity",
                "HIGH,CRITICAL",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in (0, 1) and not proc.stdout.strip():
            err = (proc.stderr or "trivy failed").strip()
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes=f"trivy error: {err}",
            )

        try:
            report = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="trivy returned non-JSON output",
            )

        critical: list[str] = []
        high: list[str] = []
        for result in report.get("Results", []) or []:
            if not isinstance(result, dict):
                continue
            for mis in result.get("Misconfigurations", []) or []:
                if not isinstance(mis, dict):
                    continue
                sev = str(mis.get("Severity", "")).upper()
                title = str(mis.get("Title", mis.get("ID", "finding")))
                if sev == "CRITICAL":
                    critical.append(title)
                elif sev == "HIGH":
                    high.append(title)

        if critical:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                findings=tuple(critical),
                notes=f"{len(critical)} CRITICAL finding(s)",
            )
        if high:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                findings=tuple(high),
                notes=f"{len(high)} HIGH finding(s)",
            )
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS,
            notes="No HIGH or CRITICAL findings.",
        )


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


__all__ = [
    "IaCAmbiguityGate",
    "PlanDiffFinding",
    "PlanDiffGate",
    "SecurityBaselineGate",
]
