"""CLI draft-corpus command tests for pickled-diff."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_diff.cli import main
from pickled_diff.drafter import RATIONALE_SENTINEL

_VALID_CORPUS = json.dumps(
    [
        {"name": "empty", "payload": ""},
        {"name": "one", "payload": "1"},
    ]
)


class _CannedDiffLLM(LLMClient):
    provider_key = "canned"

    def __init__(self, response: str) -> None:
        self._response = response

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
        _ = messages, model, max_tokens, temperature, stop, extras
        return Completion(
            text=self._response,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


class _RaisingDiffLLM(LLMClient):
    provider_key = "canned"

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
        _ = messages, model, max_tokens, temperature, stop, extras
        msg = "LLM complete failed"
        raise RuntimeError(msg)

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


def _fake_diff_llm() -> LLMClient:
    body = f"{_VALID_CORPUS}\n{RATIONALE_SENTINEL}\nok\n"
    return _CannedDiffLLM(body)


def test_draft_writes_artifact_to_stdout_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("pickled_diff.cli._build_llm_client", _fake_diff_llm)
    seeds = tmp_path / "seeds.json"
    seeds.write_text('[{"name": "a", "payload": "1"}]', encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft-corpus", "--seeds", str(seeds), "--target-size", "2"],
    )
    assert result.exit_code == 0
    parsed = json.loads(result.output)
    assert len(parsed) == 2


def test_draft_writes_artifact_to_output_file_with_dash_o(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("pickled_diff.cli._build_llm_client", _fake_diff_llm)
    seeds = tmp_path / "seeds.json"
    seeds.write_text('[{"name": "a", "payload": "1"}]', encoding="utf-8")
    out = tmp_path / "corpus.json"
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft-corpus",
            "--seeds",
            str(seeds),
            "--target-size",
            "2",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert len(json.loads(out.read_text(encoding="utf-8"))) == 2


def test_draft_exits_1_when_drafter_emits_warning(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_diff.cli._build_llm_client",
        lambda: _CannedDiffLLM("not-json"),
    )
    seeds = tmp_path / "seeds.json"
    seeds.write_text("[]", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft-corpus", "--seeds", str(seeds), "--target-size", "2"],
    )
    assert result.exit_code == 1
    assert "warning:" in result.stderr


def test_draft_exits_2_on_drafter_exception(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_diff.cli._build_llm_client",
        lambda: _RaisingDiffLLM(),
    )
    seeds = tmp_path / "seeds.json"
    seeds.write_text("[]", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft-corpus", "--seeds", str(seeds), "--target-size", "2"],
    )
    assert result.exit_code == 2
