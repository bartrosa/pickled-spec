"""Parse-safe tag injection tests (friction #16)."""

from __future__ import annotations

import tempfile
from pathlib import Path

import yaml
from pickled_bdd.adapters.pytest_bdd import PytestBddAdapter
from pickled_core.mine.tag_stage import (
    apply_line_based_tags,
    repair_split_scenario_tags,
    resolve_ruleset_sources,
    run_tag,
)

_CORRUPTED_SHAPE = (
    "Feature: draft\n\n"
    "  Sc@bdd-domain:draft-output-parses-via-pytest-bdd\n"
    "ario: first scenario\n"
    "    Given a\n\n"
    "  Scena@bdd-domain:draft-warnings-field-populated-on-failure\n"
    "rio: second scenario\n"
    "    Given b\n"
)


def _parse_feature_text(text: str) -> None:
    with tempfile.NamedTemporaryFile(suffix=".feature", delete=False) as handle:
        path = Path(handle.name)
    path.write_text(text, encoding="utf-8")
    PytestBddAdapter().parse_feature_file(path)
    path.unlink(missing_ok=True)


def _write_ruleset(path: Path, *, short_name: str, rules: list[dict[str, str]]) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "metadata": {
                    "source_id": "TEST",
                    "source_title": "Test",
                    "applies_to": "test",
                    "maintainer": "test",
                    "source_version": "0.1",
                    "active_from": "2026-05-25",
                },
                "rules": rules,
            }
        ),
        encoding="utf-8",
    )


def test_tag_inserted_as_line_above_scenario() -> None:
    before = "Feature: x\n\n  Scenario: reset password\n    Given a user\n"
    after = apply_line_based_tags(before, [(2, ["@team:rule-a"])])
    lines = after.splitlines()
    assert lines[2] == "  @team:rule-a"
    assert lines[3] == "  Scenario: reset password"
    _parse_feature_text(after)


def test_tag_indentation_matches_scenario() -> None:
    before = "Feature: x\n\n    Scenario: deep indent\n      Given x\n"
    after = apply_line_based_tags(before, [(2, ["@team:rule-a"])])
    assert after.splitlines()[2] == "    @team:rule-a"
    assert after.splitlines()[3] == "    Scenario: deep indent"
    _parse_feature_text(after)


def test_no_tag_spliced_into_keyword() -> None:
    before = (
        "Feature: x\n\n"
        "  Scenario: one\n    Given a\n\n"
        "  Scenario: two\n    Given b\n"
    )
    after = apply_line_based_tags(
        before,
        [(2, ["@bdd-domain:rule-x"]), (4, ["@bdd-domain:rule-y"])],
    )
    assert "Sc@" not in after
    assert after.count("  Scenario:") == 2
    _parse_feature_text(after)


def test_duplicate_tags_deduped() -> None:
    before = "Feature: x\n\n  @team:rule-a\n  Scenario: already tagged\n    Given x\n"
    after = apply_line_based_tags(
        before,
        [(3, ["@team:rule-a", "@team:rule-a", "@team:rule-b"])],
    )
    tag_lines = [line for line in after.splitlines() if line.strip().startswith("@")]
    assert tag_lines.count("  @team:rule-a") == 1
    assert tag_lines.count("  @team:rule-b") == 1
    _parse_feature_text(after)


def test_tags_scoped_per_scenario() -> None:
    before = (
        "Feature: x\n\n"
        "  Scenario: first uses cache\n    Given disk cache\n\n"
        "  Scenario: second uses password\n    Given password reset\n"
    )
    after = apply_line_based_tags(
        before,
        [
            (2, ["@team:cache-disk"]),
            (5, ["@team:password-policy"]),
        ],
    )
    lines = after.splitlines()
    first_tag_idx = lines.index("  @team:cache-disk")
    second_tag_idx = lines.index("  @team:password-policy")
    assert first_tag_idx < lines.index("  Scenario: first uses cache")
    assert second_tag_idx < lines.index("  Scenario: second uses password")
    assert "@team:password-policy" not in lines[first_tag_idx : second_tag_idx]
    assert "@team:cache-disk" not in lines[second_tag_idx:]
    _parse_feature_text(after)


def test_cross_feature_no_bleed(tmp_path: Path) -> None:
    feature_a = "Feature: A\n\n  Scenario: cache story\n    Given disk cache\n"
    feature_b = "Feature: B\n\n  Scenario: password story\n    Given password token\n"
    tagged_a = apply_line_based_tags(feature_a, [(2, ["@team:cache-disk"])])
    tagged_b = apply_line_based_tags(feature_b, [(2, ["@team:password-policy"])])
    assert "@team:password-policy" not in tagged_a
    assert "@team:cache-disk" not in tagged_b
    _parse_feature_text(tagged_a)
    _parse_feature_text(tagged_b)


def test_scenario_outline_tags_above_not_inside() -> None:
    before = (
        "Feature: outline\n\n"
        "  Scenario Outline: matrix\n"
        "    Given <x>\n"
        "    Examples:\n"
        "      | x |\n"
        "      | 1 |\n"
    )
    after = apply_line_based_tags(before, [(2, ["@team:rule-a"])])
    lines = after.splitlines()
    assert lines[2] == "  @team:rule-a"
    assert lines[3] == "  Scenario Outline: matrix"
    assert lines[5] == "    Examples:"
    _parse_feature_text(after)


def test_existing_feature_tags_preserved() -> None:
    before = (
        "@feature-level\n"
        "Feature: tagged\n\n"
        "  @existing\n"
        "  Scenario: one\n"
        "    Given a\n"
    )
    after = apply_line_based_tags(before, [(4, ["@team:new-rule"])])
    assert "@feature-level" in after
    assert "  @existing" in after
    assert "  @team:new-rule" in after
    _parse_feature_text(after)


def test_injection_idempotent() -> None:
    before = "Feature: x\n\n  Scenario: one\n    Given a\n"
    once = apply_line_based_tags(before, [(2, ["@team:rule-a"])])
    twice = apply_line_based_tags(once, [(2, ["@team:rule-a"])])
    assert once == twice


def test_every_proposed_tag_references_real_rule(tmp_path: Path) -> None:
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    _write_ruleset(
        rules_dir / "team.yaml",
        short_name="team",
        rules=[
            {
                "id": "cache-disk",
                "title": "Identical LLM inputs use disk cache",
                "description": "cache",
                "enforcement": "strict",
            }
        ],
    )
    features = tmp_path / "features"
    features.mkdir()
    (features / "demo.feature").write_text(
        "Feature: demo\n\n  Scenario: uses disk cache\n    Given cache\n",
        encoding="utf-8",
    )
    sources = resolve_ruleset_sources(tmp_path, ruleset_config=None, ruleset_dir=rules_dir)
    assert sources is not None
    run_tag(tmp_path, ruleset_sources=sources, quick=True)
    text = (features / "demo.feature").read_text(encoding="utf-8")
    assert "@team:cache-disk" in text
    _parse_feature_text(text)


def test_all_repo_features_reparse_after_tagging() -> None:
    repaired = repair_split_scenario_tags(_CORRUPTED_SHAPE)
    assert "Sc@" not in repaired
    _parse_feature_text(repaired)
    fresh = (
        "Feature: draft\n\n"
        "  Scenario: first scenario\n    Given a\n\n"
        "  Scenario: second scenario\n    Given b\n"
    )
    tagged = apply_line_based_tags(
        fresh,
        [
            (2, ["@bdd-domain:draft-output-parses-via-pytest-bdd"]),
            (5, ["@bdd-domain:draft-warnings-field-populated-on-failure"]),
        ],
    )
    assert "Sc@" not in tagged
    _parse_feature_text(tagged)
