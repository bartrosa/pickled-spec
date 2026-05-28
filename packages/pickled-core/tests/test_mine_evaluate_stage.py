"""Tests for mine evaluate stage."""

from __future__ import annotations

import json
import shutil
from collections.abc import Mapping
from pathlib import Path
from typing import Any

import pytest
from pickled_core import GateResult, Verdict
from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_core.mine.errors import MissingStageInputError
from pickled_core.mine.evaluate_stage import run_evaluate
from pickled_core.mine.tag_stage import resolve_ruleset_sources

_FIXTURE_RULESET = (
    Path(__file__).resolve().parents[2]
    / "pickled-rules"
    / "tests"
    / "fixtures"
    / "tiny_ruleset.yaml"
)


def _write_ruleset_config(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "team.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        "ruleset: ./rulesets/team.yaml\nruleset_short_name: team-rules\n",
        encoding="utf-8",
    )


def _feature_with_tags(tmp_path: Path) -> Path:
    features = tmp_path / "features"
    features.mkdir()
    path = features / "demo.feature"
    path.write_text(
        """\
Feature: demo

  @team-rules:1.1
  @team-rules:1.2
  Scenario: covers strict rules
    Given x
""",
        encoding="utf-8",
    )
    return path


def test_coverage_written_per_ruleset(tmp_path: Path) -> None:
    _write_ruleset_config(tmp_path)
    _feature_with_tags(tmp_path)
    sources = resolve_ruleset_sources(tmp_path, ruleset_config=None, ruleset_dir=None)
    assert sources is not None
    result = run_evaluate(tmp_path, ruleset_sources=sources, llm=None)
    data = json.loads(result.coverage_path.read_text(encoding="utf-8"))
    assert data["rulesets"]
    assert data["rulesets"][0]["short_name"] == "team-rules"


def test_evaluate_skips_unparseable_feature(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter

    features = tmp_path / "features"
    features.mkdir()
    (features / "broken.feature").write_text(
        "Feature: bad\n\n  Scenario: ok\n    Given a\n",
        encoding="utf-8",
    )
    _write_ruleset_config(tmp_path)
    sources = resolve_ruleset_sources(tmp_path, ruleset_config=None, ruleset_dir=None)

    def _fail_parse(_self: PytestBddAdapter, path: Path) -> object:
        _ = _self
        msg = f"parse failed: {path.name}"
        raise ValueError(msg)

    monkeypatch.setattr(PytestBddAdapter, "parse_feature_file", _fail_parse)
    result = run_evaluate(tmp_path, ruleset_sources=sources, llm=None)
    err = capsys.readouterr().err
    assert "skip unparseable" in err
    assert result.coverage_path.is_file()


def test_ambiguity_skips_cleanly_without_llm(tmp_path: Path) -> None:
    _feature_with_tags(tmp_path)
    result = run_evaluate(tmp_path, ruleset_sources=None, llm=None)
    data = json.loads(result.ambiguity_path.read_text(encoding="utf-8"))
    assert data["features"][0]["skipped"] is True
    assert data["features"][0]["verdict"] == "pass"


class _FailAmbiguityLLM(LLMClient):
    provider_key = "fake"

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1

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
        payload = (
            '{"ambiguous": true, "alternatives": ["alt a", "alt b"], '
            '"suggested_fix": "tighten steps"}'
        )
        return Completion(
            text=payload,
            usage=TokenUsage(input=1, output=1),
            model_id_resolved="fake",
            raw_response=None,
        )


def test_ambiguity_records_findings_with_canned_fail(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _feature_with_tags(tmp_path)

    def _fake_run(path: Path, llm: LLMClient | None) -> GateResult:
        _ = path, llm
        from pickled_core import AmbiguityFinding

        return GateResult(
            gate_name="ambiguity",
            verdict=Verdict.FAIL,
            findings=(
                AmbiguityFinding(
                    target_name="covers strict rules",
                    alternatives=("alt a", "alt b"),
                    suggested_fix="tighten",
                ),
            ),
            notes="ambiguous",
        )

    monkeypatch.setattr(
        "pickled_core.mine.evaluate_stage._import_run_ambiguity_gate",
        lambda: _fake_run,
    )
    result = run_evaluate(tmp_path, ruleset_sources=None, llm=_FailAmbiguityLLM())
    data = json.loads(result.ambiguity_path.read_text(encoding="utf-8"))
    assert data["features"][0]["verdict"] == "fail"
    assert data["features"][0]["finding_count"] == 1


def test_evaluate_respects_surfaces_filter(tmp_path: Path) -> None:
    features = tmp_path / "features"
    features.mkdir()
    (features / "tiny_target_greet.feature").write_text(
        "Feature: greet\n\n  Scenario: one\n    Given x\n",
        encoding="utf-8",
    )
    (features / "other_pkg_ping.feature").write_text(
        "Feature: ping\n\n  Scenario: two\n    Given y\n",
        encoding="utf-8",
    )
    result = run_evaluate(tmp_path, ruleset_sources=None, llm=None, surfaces=("greet",))
    paths = {entry.feature_path for entry in result.ambiguity}
    assert paths == {"features/tiny_target_greet.feature"}


def test_evaluate_missing_features_raises_actionable_error(tmp_path: Path) -> None:
    with pytest.raises(MissingStageInputError, match="mine features"):
        run_evaluate(tmp_path, ruleset_sources=None, llm=None)
