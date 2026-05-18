from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pickled_rules import RuleSetValidationError, load_ruleset

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_ruleset.yaml"


def test_load_tiny_ruleset() -> None:
    rs = load_ruleset(FIXTURE)
    assert rs.source_id == "TEST-RULESET"
    assert rs.applies_to == "global"
    assert rs.active_from == date(2025, 1, 1)
    assert len(rs.rules) == 2
    assert rs.rules[0].enforcement == "strict"


def test_ruleset_find_by_id() -> None:
    rs = load_ruleset(FIXTURE)
    assert rs.find("1.2") is not None
    assert rs.find("99") is None


def test_ruleset_as_references() -> None:
    rs = load_ruleset(FIXTURE)
    refs = rs.as_references()
    assert len(refs) == 2
    assert refs[0].source_id == "TEST-RULESET(1.1)"
    assert refs[0].description == "The first rule has some text."


def test_missing_metadata_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("rules: []\n", encoding="utf-8")
    with pytest.raises(RuleSetValidationError, match="Missing required key 'metadata'"):
        load_ruleset(p)


def test_invalid_enforcement_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  applies_to: "g"
  maintainer: "m"
  source_version: "1"
  active_from: "2025-01-01"
rules:
  - id: "1"
    title: "t"
    description: "body"
    enforcement: "foo"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(RuleSetValidationError, match="Invalid enforcement"):
        load_ruleset(p)


def test_malformed_yaml_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("{ not valid yaml [[[\n", encoding="utf-8")
    with pytest.raises(RuleSetValidationError, match="Malformed YAML"):
        load_ruleset(p)


def test_invalid_date_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  applies_to: "g"
  maintainer: "m"
  source_version: "1"
  active_from: "not-a-date"
rules: []
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(RuleSetValidationError, match="Invalid ISO date"):
        load_ruleset(p)
