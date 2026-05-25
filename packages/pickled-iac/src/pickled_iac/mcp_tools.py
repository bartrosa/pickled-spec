"""MCP tool registration for pickled-iac."""

from __future__ import annotations

import json
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from fastmcp import FastMCP

from pickled_core import LLMClient

from pickled_iac.advisor import IaCAdvisor
from pickled_iac.drafter import IaCDrafter
from pickled_iac.gates import PlanDiffFinding, PlanDiffGate
from pickled_iac.oracle import validate_files


def register_with_fastmcp(app: FastMCP, *, llm: LLMClient | None = None) -> None:
    @app.tool(name="draft_terraform_module")
    def draft_terraform_module(
        *,
        user_story: str,
        provider: str = "aws",
    ) -> dict[str, Any]:
        """Draft a Terraform module from a user story."""
        if llm is None:
            msg = (
                "LLM client not configured (set pickled.config.yaml or "
                "PICKLED_IAC_LLM_FACTORY)"
            )
            raise RuntimeError(msg)
        artifact = IaCDrafter(llm).draft_module(user_story, provider=provider)
        return {
            "content": artifact.content,
            "format": artifact.format,
            "path": str(artifact.path) if artifact.path else None,
        }

    @app.tool(name="validate_terraform_dir")
    def validate_terraform_dir(*, tf_files: dict[str, str]) -> dict[str, Any]:
        """Validate Terraform files written to a temp directory."""
        result = validate_files(tf_files)
        return {
            "valid": result.valid,
            "format": result.format,
            "diagnostics": result.diagnostics,
        }

    @app.tool(name="diff_terraform_plans")
    def diff_terraform_plans(
        *,
        base_plan_json: str,
        head_plan_json: str,
    ) -> dict[str, Any]:
        """Compare base vs head terraform plan JSON."""
        base_plan = json.loads(base_plan_json)
        head_plan = json.loads(head_plan_json)
        gate = PlanDiffGate()
        result = gate.run(head_plan, context={"base_plan": base_plan})
        findings = [
            {
                "address": f.address,
                "actions_before": list(f.actions_before),
                "actions_after": list(f.actions_after),
            }
            for f in result.findings
            if isinstance(f, PlanDiffFinding)
        ]
        return {
            "verdict": result.verdict.value,
            "notes": result.notes,
            "findings": findings,
        }

    @app.tool(name="explain_plan_diff")
    def explain_plan_diff(*, plan_json: str) -> dict[str, Any]:
        """Summarise a terraform plan JSON and flag risky actions."""
        if llm is None:
            msg = (
                "LLM client not configured (set pickled.config.yaml or "
                "PICKLED_IAC_LLM_FACTORY)"
            )
            raise RuntimeError(msg)
        result = IaCAdvisor(llm).explain_plan_diff(plan_json=plan_json)
        return {"text": result.text, "warnings": list(result.warnings)}

    @app.tool(name="suggest_security_remediation")
    def suggest_security_remediation(
        *,
        trivy_findings_json: str,
        hcl_text: str = "",
    ) -> dict[str, Any]:
        """Suggest HCL patches for Trivy config-scan findings."""
        if llm is None:
            msg = (
                "LLM client not configured (set pickled.config.yaml or "
                "PICKLED_IAC_LLM_FACTORY)"
            )
            raise RuntimeError(msg)
        result = IaCAdvisor(llm).suggest_security_remediation(
            trivy_findings_json=trivy_findings_json,
            hcl_text=hcl_text,
        )
        return {"text": result.text, "warnings": list(result.warnings)}


__all__ = ["register_with_fastmcp"]
