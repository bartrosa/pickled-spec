"""CLI draft command tests for pickled-data."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_data.cli import main
from pickled_data.drafter import RATIONALE_SENTINEL

_VALID_SQL = """-- intent: add deleted_at
ALTER TABLE users ADD COLUMN deleted_at TEXT;
"""


class _CannedDataLLM(LLMClient):
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


class _RaisingDataLLM(LLMClient):
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


def _fake_data_llm() -> LLMClient:
    body = f"{_VALID_SQL}\n{RATIONALE_SENTINEL}\nok\n"
    return _CannedDataLLM(body)


def test_draft_writes_artifact_to_stdout_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("pickled_data.cli._build_llm_client", _fake_data_llm)
    intent = tmp_path / "intent.txt"
    intent.write_text("add soft delete column", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft", "--intent", str(intent), "--dialect", "sqlite"],
    )
    assert result.exit_code == 0
    assert "ALTER TABLE" in result.output


def test_draft_writes_artifact_to_output_file_with_dash_o(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("pickled_data.cli._build_llm_client", _fake_data_llm)
    intent = tmp_path / "intent.txt"
    intent.write_text("intent", encoding="utf-8")
    out = tmp_path / "migration.sql"
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft",
            "--intent",
            str(intent),
            "--dialect",
            "sqlite",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert "deleted_at" in out.read_text(encoding="utf-8")


def test_draft_exits_1_when_drafter_emits_warning(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_data.cli._build_llm_client",
        lambda: _CannedDataLLM("SELECT FROM ;;"),
    )
    intent = tmp_path / "intent.txt"
    intent.write_text("x", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft", "--intent", str(intent), "--dialect", "sqlite"],
    )
    assert result.exit_code == 1
    assert "warning:" in result.stderr


def test_draft_exits_2_on_drafter_exception(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_data.cli._build_llm_client",
        lambda: _RaisingDataLLM(),
    )
    intent = tmp_path / "intent.txt"
    intent.write_text("x", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["draft", "--intent", str(intent), "--dialect", "sqlite"],
    )
    assert result.exit_code == 2
