from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner
from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_rules.cli import main
from pickled_rules.drafter import RATIONALE_SENTINEL

_DRAFT_YAML = """metadata:
  source_id: test-src
  source_title: Test Rules
  applies_to: internal-api
  maintainer: tests
  source_version: '1.0'
  active_from: '2026-05-25'
rules:
  - id: api-naming
    title: Use consistent paths
    description: REST paths use kebab-case resource names.
    enforcement: strict
"""


class _CannedRulesLLM(LLMClient):
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


class _RaisingRulesLLM(LLMClient):
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


def _fake_rules_llm() -> LLMClient:
    body = f"{_DRAFT_YAML}\n{RATIONALE_SENTINEL}\nCLI draft ok.\n"
    return _CannedRulesLLM(body)


def _warning_rules_llm() -> LLMClient:
    return _CannedRulesLLM(f"metadata: [\nrules: []\n{RATIONALE_SENTINEL}\nx\n")

PKG = Path(__file__).resolve().parent.parent
TINY = PKG / "tests" / "fixtures" / "tiny_ruleset.yaml"
PARTIAL = PKG / "tests" / "fixtures" / "partial_coverage.feature"


def test_cli_builtin_partial_coverage_fails_with_strict_gaps() -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "check",
            "--ruleset",
            "team-api-conv",
            "--feature",
            str(PARTIAL),
        ],
    )
    assert result.exit_code == 1
    out = result.stdout + result.stderr
    assert "naming.2" in out
    assert "timestamps.1" in out
    strict = out.split("## Unreferenced strict rules")[1].split("## Unreferenced advisory")[0]
    assert "naming.1" not in strict or "### `naming.1`" not in strict


def test_cli_ruleset_path_happy(tmp_path: Path) -> None:
    feat = tmp_path / "tiny_ruleset.feature"
    feat.write_text(
        "Feature: T\n  @tiny_ruleset:1.1\n  Scenario: S\n    Given x\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", str(TINY), "--feature", str(feat)],
    )
    assert r.exit_code == 0


def test_cli_quiet() -> None:
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", "team-api-conv", "--feature", str(PARTIAL), "--quiet"],
    )
    assert r.exit_code == 1
    assert r.stdout.strip().startswith("FAIL:")
    assert "# Coverage report" not in r.stdout


def test_cli_feature_level_tags(tmp_path: Path) -> None:
    feat = tmp_path / "feature_tag.feature"
    feat.write_text(
        "@team-api-conv:errors.1\n"
        "Feature: Error handling\n"
        "\n"
        "  Scenario: Problem details returned\n"
        "    Given an invalid request\n"
        "    Then the response is problem+json\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["check", "--ruleset", "team-api-conv", "--feature", str(feat)],
    )
    out = result.stdout + result.stderr
    strict = out.split("## Unreferenced strict rules")
    assert len(strict) > 1
    gaps = strict[1].split("## Unreferenced advisory")[0]
    assert "### `errors.1`" not in gaps
    table = out.split("## Referenced rules")[1].split("## ")[0]
    assert "`errors.1`" in table and "✅" in table


def test_draft_writes_artifact_to_stdout_by_default(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_rules.cli._build_llm_client",
        _fake_rules_llm,
    )
    brief = tmp_path / "brief.txt"
    brief.write_text("API naming rules", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft",
            "--brief",
            str(brief),
            "--short-name",
            "api",
            "--source-id",
            "test-src",
            "--applies-to",
            "internal-api",
            "--active-from",
            "2026-05-25",
        ],
    )
    assert result.exit_code == 0
    assert "api-naming:" in result.output or "api-naming" in result.output


def test_draft_writes_artifact_to_output_file_with_dash_o(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_rules.cli._build_llm_client",
        _fake_rules_llm,
    )
    brief = tmp_path / "brief.txt"
    brief.write_text("brief", encoding="utf-8")
    out = tmp_path / "rules.yaml"
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft",
            "--brief",
            str(brief),
            "--short-name",
            "api",
            "--source-id",
            "test-src",
            "--applies-to",
            "internal-api",
            "--active-from",
            "2026-05-25",
            "-o",
            str(out),
        ],
    )
    assert result.exit_code == 0
    assert out.is_file()
    assert "api-naming" in out.read_text(encoding="utf-8")


def test_draft_exits_1_when_drafter_emits_warning(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_rules.cli._build_llm_client",
        _warning_rules_llm,
    )
    brief = tmp_path / "brief.txt"
    brief.write_text("brief", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft",
            "--brief",
            str(brief),
            "--short-name",
            "api",
            "--source-id",
            "test-src",
            "--applies-to",
            "internal-api",
            "--active-from",
            "2026-05-25",
        ],
    )
    assert result.exit_code == 1
    assert "warning:" in result.stderr


def test_draft_exits_2_on_drafter_exception(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr(
        "pickled_rules.cli._build_llm_client",
        lambda: _RaisingRulesLLM(),
    )
    brief = tmp_path / "brief.txt"
    brief.write_text("brief", encoding="utf-8")
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "draft",
            "--brief",
            str(brief),
            "--short-name",
            "api",
            "--source-id",
            "test-src",
            "--applies-to",
            "internal-api",
            "--active-from",
            "2026-05-25",
        ],
    )
    assert result.exit_code == 2


def test_cli_rule_block_scenario(tmp_path: Path) -> None:
    feat = tmp_path / "rule.feature"
    feat.write_text(
        "Feature: T\n  Rule: Covers 1.1\n    @tiny_ruleset:1.1\n    Scenario: S\n      Given x\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", str(TINY), "--feature", str(feat)],
    )
    assert r.exit_code == 0, r.stdout + r.stderr
