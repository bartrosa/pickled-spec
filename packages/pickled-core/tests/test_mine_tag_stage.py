"""Tests for mine tag stage."""

from __future__ import annotations

import json
from pathlib import Path

import yaml
from pickled_core.mine.tag_stage import (
    repair_split_scenario_tags,
    resolve_ruleset_sources,
    run_tag,
)

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"

def _write_minimal_ruleset(path: Path) -> None:
    path.write_text(
        yaml.safe_dump(
            {
                "metadata": {
                    "source_id": "TEST",
                    "source_title": "Test rules",
                    "applies_to": "test",
                    "maintainer": "test",
                    "source_version": "0.1",
                    "active_from": "2026-05-25",
                },
                "rules": [
                    {
                        "id": "cache-disk",
                        "title": "Identical LLM inputs use disk cache",
                        "description": "cache",
                        "enforcement": "strict",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )


def test_resolve_ruleset_config_relative_to_config_dir(tmp_path: Path) -> None:
    cfg_dir = tmp_path / "dogfood"
    rules_dir = cfg_dir / "rulesets"
    rules_dir.mkdir(parents=True)
    rules_path = rules_dir / "internal.yaml"
    _write_minimal_ruleset(rules_path)
    cfg_path = cfg_dir / "pickled.ruleset.yaml"
    cfg_path.write_text(
        "rulesets:\n  - path: ./rulesets/internal.yaml\n    short_name: pickled-internal\n",
        encoding="utf-8",
    )
    sources = resolve_ruleset_sources(
        tmp_path,
        ruleset_config=cfg_path,
        ruleset_dir=None,
    )
    assert sources is not None
    assert len(sources.rulesets) == 1
    assert sources.rulesets[0].path == rules_path.resolve()


def test_run_tag_writes_proposals(tmp_path: Path) -> None:
    features = tmp_path / "features"
    features.mkdir()
    feature_text = (
        "Feature: greet\n\n"
        "  Scenario: greet by name\n"
        "    Given a user\n"
        "    When they greet\n"
        "    Then ok\n"
    )
    (features / "tiny_target_greet.feature").write_text(feature_text, encoding="utf-8")
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    _write_minimal_ruleset(rules_dir / "internal.yaml")
    sources = resolve_ruleset_sources(
        tmp_path,
        ruleset_config=None,
        ruleset_dir=rules_dir,
    )
    result = run_tag(tmp_path, ruleset_sources=sources, quick=True)
    assert not result.skipped
    assert result.proposals_path.is_file()
    data = json.loads(result.proposals_path.read_text(encoding="utf-8"))
    assert data["features"]


def test_repair_split_scenario_tags() -> None:
    broken = (
        "Feature: x\n\n"
        "  Sc@bdd-domain:gherkin-feature-header-required\n"
        "enario: whitespace story\n\n"
        "  Scenar@bdd-domain:draft-empty-story-deterministic-failure\n"
        "io: gate failure\n\n"
        "  Scenario@bdd-domain:draft-empty-story-deterministic-failure\n"
        ": empty story\n"
    )
    fixed = repair_split_scenario_tags(broken)
    assert "Sc@" not in fixed
    assert "  @bdd-domain:gherkin-feature-header-required\n" in fixed
    assert "  Scenario: whitespace story\n" in fixed
    assert "  Scenario: gate failure\n" in fixed
    assert "  Scenario: empty story\n" in fixed


def test_tag_respects_surfaces_filter(tmp_path: Path) -> None:
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
    rules_dir = tmp_path / "rulesets"
    rules_dir.mkdir()
    _write_minimal_ruleset(rules_dir / "internal.yaml")
    sources = resolve_ruleset_sources(
        tmp_path,
        ruleset_config=None,
        ruleset_dir=rules_dir,
    )
    result = run_tag(tmp_path, ruleset_sources=sources, quick=True, surfaces=("greet",))
    data = json.loads(result.proposals_path.read_text(encoding="utf-8"))
    paths = {entry["feature_path"] for entry in data["features"]}
    assert paths == {"features/tiny_target_greet.feature"}
