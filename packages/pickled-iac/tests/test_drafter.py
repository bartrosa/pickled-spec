from __future__ import annotations

from collections.abc import Mapping
from typing import Any
from unittest.mock import patch

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_iac.drafter import IaCDrafter
from pickled_iac.types import ValidateResult


class FakeLLMClient(LLMClient):
    provider_key = "fake"

    def __init__(self, response: str) -> None:
        self.response = response

    def complete(
        self,
        *,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float | None,
        stop: list[str] | None,
        extras: Mapping[str, Any] | None,
    ) -> Completion:
        _ = model, max_tokens, temperature, stop, extras
        return Completion(
            text=self.response,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


_VALID_TF = """
resource "aws_s3_bucket" "x" {
  bucket = "example"
}
"""


def test_drafter_returns_artifact_when_validate_passes() -> None:
    fake = FakeLLMClient(_VALID_TF)
    with (
        patch("pickled_iac.drafter.validate", return_value=ValidateResult(valid=True)),
        patch("pickled_iac.drafter.iac_binary", return_value="terraform"),
        patch("pickled_iac.drafter.iac_format", return_value="terraform"),
    ):
        artifact = IaCDrafter(fake).draft_module("Need a bucket", provider="aws")
    assert "aws_s3_bucket" in artifact.content
    assert artifact.format == "terraform"


def test_drafter_uses_opentofu_label_when_only_tofu_on_path() -> None:
    """OpenTofu's binary is ``tofu``; format label stays ``opentofu``."""
    fake = FakeLLMClient(_VALID_TF)
    with (
        patch("pickled_iac.drafter.validate", return_value=ValidateResult(valid=True)),
        patch("pickled_iac.drafter.iac_binary", return_value="tofu"),
        patch("pickled_iac.drafter.iac_format", return_value="opentofu"),
    ):
        artifact = IaCDrafter(fake).draft_module("Need a bucket", provider="aws")
    assert artifact.format == "opentofu"
