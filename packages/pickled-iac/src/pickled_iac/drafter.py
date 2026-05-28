"""LLM-driven Terraform module drafter."""

from __future__ import annotations

import tempfile
from pathlib import Path

from pickled_core import LLMClient, PromptTemplate
from pickled_core.llm.sanitize import strip_markdown_fence
from pickled_core.llm.turns import complete_prompt

from pickled_iac.oracle import iac_binary, validate
from pickled_iac.types import IaCArtifact


def _prompt_path(name: str) -> Path:
    return Path(__file__).resolve().parent / "prompts" / name


class IaCDrafter:
    """Draft a Terraform module from a natural-language user story."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(_prompt_path("draft.md"))

    def draft_module(
        self,
        user_story: str,
        provider: str = "aws",
    ) -> IaCArtifact:
        """Draft, validate in a temp dir, and return an IaCArtifact."""
        binary = iac_binary()
        fmt: str = "opentofu" if binary == "opentofu" else "terraform"
        last_error = ""

        for _attempt in range(3):
            feedback = (
                f"\n\nPrevious validation errors:\n{last_error}" if last_error else ""
            )
            prompt = self._template.render(
                provider=provider,
                user_story=user_story,
                error_feedback=feedback,
            )
            hcl = strip_markdown_fence(
                complete_prompt(
                    self._llm,
                    prompt,
                    system="Output only Terraform HCL. No fences, no commentary.",
                )
            )

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "main.tf").write_text(hcl, encoding="utf-8")
                result = validate(root)
            if result.valid:
                return IaCArtifact(content=hcl, format=fmt, path=None)  # type: ignore[arg-type]
            last_error = "; ".join(result.diagnostics) or "validation failed"

        msg = f"failed to draft valid Terraform after 3 attempts: {last_error}"
        raise RuntimeError(msg)


__all__ = ["IaCDrafter"]
