"""Tests for multi-ruleset workspace configuration in gates_runner."""

from __future__ import annotations

import shutil
from pathlib import Path

from pickled_core import Verdict
from pickled_rules.gates_runner import run_all

_FIXTURE_RULESET = Path(__file__).resolve().parent / "fixtures" / "tiny_ruleset.yaml"

_FEATURE_PASS = """\
Feature: Workspace coverage

  @{short}:1.1
  @{short}:1.2
  Scenario: Reference strict rules
    Given a precondition
"""


def _write_workspace(
    tmp_path: Path,
    *,
    config_yaml: str,
    short_name: str = "team-rules",
) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "rs.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(config_yaml, encoding="utf-8")
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "test.feature").write_text(
        _FEATURE_PASS.format(short=short_name),
        encoding="utf-8",
    )


def test_single_ruleset_key_still_works(tmp_path: Path) -> None:
    _write_workspace(
        tmp_path,
        config_yaml="ruleset: ./rulesets/rs.yaml\nruleset_short_name: team-rules\n",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].gate_name == "rules.coverage"
    assert results[0].verdict == Verdict.PASS


def test_plural_rulesets_key_yields_namespaced_gates(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "alpha.yaml")
    shutil.copy(_FIXTURE_RULESET, rules_dir / "beta.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        """\
rulesets:
  - path: ./rulesets/alpha.yaml
    short_name: alpha
  - path: ./rulesets/beta.yaml
    short_name: beta
""",
        encoding="utf-8",
    )
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "test.feature").write_text(
        """\
Feature: Multi ruleset coverage

  @alpha:1.1
  @alpha:1.2
  @beta:1.1
  @beta:1.2
  Scenario: Reference both rule sets
    Given a precondition
""",
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 2
    names = {r.gate_name for r in results}
    assert names == {"rules.coverage.alpha", "rules.coverage.beta"}
    assert all(r.verdict == Verdict.PASS for r in results)


def test_both_keys_fails_with_clear_message(tmp_path: Path) -> None:
    _write_workspace(
        tmp_path,
        config_yaml=(
            "ruleset: ./rulesets/rs.yaml\n"
            "rulesets:\n"
            "  - path: ./rulesets/rs.yaml\n"
        ),
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].gate_name == "rules.coverage"
    assert results[0].verdict == Verdict.FAIL
    assert "mutually exclusive" in results[0].notes


def test_duplicate_short_name_fails(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "a.yaml")
    shutil.copy(_FIXTURE_RULESET, rules_dir / "b.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        """\
rulesets:
  - path: ./rulesets/a.yaml
    short_name: same
  - path: ./rulesets/b.yaml
    short_name: same
""",
        encoding="utf-8",
    )
    (tmp_path / "features").mkdir()
    (tmp_path / "features" / "test.feature").write_text(
        _FEATURE_PASS.format(short="same"),
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].verdict == Verdict.FAIL
    assert "duplicate short_name" in results[0].notes


def test_missing_ruleset_file_one_failure_others_succeed(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "first.yaml")
    shutil.copy(_FIXTURE_RULESET, rules_dir / "third.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        """\
rulesets:
  - path: ./rulesets/first.yaml
    short_name: first
  - path: ./rulesets/missing.yaml
    short_name: middle
  - path: ./rulesets/third.yaml
    short_name: third
""",
        encoding="utf-8",
    )
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "test.feature").write_text(
        """\
Feature: Partial missing ruleset

  @first:1.1
  @first:1.2
  @third:1.1
  @third:1.2
  Scenario: Cover available rule sets
    Given a precondition
""",
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 3
    by_name = {r.gate_name: r for r in results}
    assert by_name["rules.coverage.first"].verdict == Verdict.PASS
    assert by_name["rules.coverage.middle"].verdict == Verdict.FAIL
    assert "ruleset not found" in by_name["rules.coverage.middle"].notes
    assert by_name["rules.coverage.third"].verdict == Verdict.PASS


def test_short_name_defaults_to_path_stem(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "my-stem.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        """\
rulesets:
  - path: ./rulesets/my-stem.yaml
""",
        encoding="utf-8",
    )
    features_dir = tmp_path / "features"
    features_dir.mkdir()
    (features_dir / "test.feature").write_text(
        _FEATURE_PASS.format(short="my-stem"),
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].gate_name == "rules.coverage"
    assert results[0].verdict == Verdict.PASS


def test_empty_rulesets_list_fails_validation(tmp_path: Path) -> None:
    (tmp_path / "pickled.ruleset.yaml").write_text("rulesets: []\n", encoding="utf-8")
    (tmp_path / "features").mkdir()
    (tmp_path / "features" / "test.feature").write_text(
        _FEATURE_PASS.format(short="x"),
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].verdict == Verdict.FAIL
    assert "at least one ruleset entry required" in results[0].notes


def test_default_feature_glob_unchanged(tmp_path: Path) -> None:
    _write_workspace(
        tmp_path,
        config_yaml="ruleset: ./rulesets/rs.yaml\nruleset_short_name: team-rules\n",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].verdict == Verdict.PASS


def test_custom_feature_glob_finds_features_in_subdir(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    shutil.copy(_FIXTURE_RULESET, rules_dir / "rs.yaml")
    (tmp_path / "pickled.ruleset.yaml").write_text(
        """\
ruleset: ./rulesets/rs.yaml
ruleset_short_name: team-rules
feature_glob: bdd/features/**/*.feature
""",
        encoding="utf-8",
    )
    bdd_features = tmp_path / "bdd" / "features"
    bdd_features.mkdir(parents=True)
    (bdd_features / "nested.feature").write_text(
        _FEATURE_PASS.format(short="team-rules"),
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].verdict == Verdict.PASS


def test_non_mapping_entry_fails_validation(tmp_path: Path) -> None:
    (tmp_path / "pickled.ruleset.yaml").write_text(
        'rulesets: ["bad-string"]\n',
        encoding="utf-8",
    )
    (tmp_path / "features").mkdir()
    (tmp_path / "features" / "test.feature").write_text(
        _FEATURE_PASS.format(short="x"),
        encoding="utf-8",
    )
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].verdict == Verdict.FAIL
    assert "rulesets[0]" in results[0].notes
