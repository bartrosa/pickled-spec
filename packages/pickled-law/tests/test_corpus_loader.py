from __future__ import annotations

from datetime import date
from pathlib import Path

import pytest
from pickled_law import CorpusValidationError, load_corpus

FIXTURE = Path(__file__).parent / "fixtures" / "tiny_corpus.yaml"


def test_load_tiny_corpus() -> None:
    c = load_corpus(FIXTURE)
    assert c.source_id == "TEST-CORPUS"
    assert c.source_title == "Tiny Test Corpus"
    assert c.jurisdiction == "global"
    assert c.authority == "pickled-law tests"
    assert c.source_version == "1.0"
    assert c.effective_from == date(2025, 1, 1)
    assert c.source_url == "https://example.com/test"
    assert len(c.rules) == 2
    assert c.rules[0].id == "1.1"
    assert c.rules[0].obligation == "required"
    assert c.rules[1].id == "1.2"
    assert c.rules[1].parent == "1.1"
    assert len(c.rules[1].relations) == 1
    assert c.rules[1].relations[0].kind == "requires_implementation_of"
    assert c.rules[1].relations[0].targets == ("1.1",)


def test_corpus_find_by_id() -> None:
    c = load_corpus(FIXTURE)
    r = c.find("1.2")
    assert r is not None
    assert r.title == "Second rule"
    assert c.find("99") is None


def test_corpus_as_citations() -> None:
    c = load_corpus(FIXTURE)
    cites = c.as_citations()
    assert len(cites) == 2
    assert cites[0].source_id == "TEST-CORPUS(1.1)"
    assert cites[0].locator == "1.1"
    assert cites[0].canonical_text == "The first rule has some text."
    assert cites[1].source_id == "TEST-CORPUS(1.2)"


def test_missing_metadata_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("rules: []\n", encoding="utf-8")
    with pytest.raises(CorpusValidationError, match="Missing required key 'metadata'"):
        load_corpus(p)


def test_invalid_obligation_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  jurisdiction: "g"
  authority: "a"
  source_version: "1"
  effective_from: "2025-01-01"
rules:
  - id: "1"
    title: "t"
    text: "body"
    obligation: "foo"
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(CorpusValidationError, match="Invalid obligation.*foo"):
        load_corpus(p)


def test_malformed_yaml_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text("{ not valid yaml [[[\n", encoding="utf-8")
    with pytest.raises(CorpusValidationError, match="Malformed YAML"):
        load_corpus(p)


def test_corpus_short_name_loaded_when_declared(tmp_path: Path) -> None:
    p = tmp_path / "with_short.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  jurisdiction: "g"
  authority: "a"
  source_version: "1"
  effective_from: "2025-01-01"
  short_name: "HiPaA"
rules: []
""".strip(),
        encoding="utf-8",
    )
    c = load_corpus(p)
    assert c.short_name == "hipaa"


def test_corpus_short_name_optional(tmp_path: Path) -> None:
    p = tmp_path / "no_short.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  jurisdiction: "g"
  authority: "a"
  source_version: "1"
  effective_from: "2025-01-01"
rules: []
""".strip(),
        encoding="utf-8",
    )
    c = load_corpus(p)
    assert c.short_name is None


def test_invalid_date_raises(tmp_path: Path) -> None:
    p = tmp_path / "bad.yaml"
    p.write_text(
        """
metadata:
  source_id: "X"
  source_title: "T"
  jurisdiction: "g"
  authority: "a"
  source_version: "1"
  effective_from: "not-a-date"
rules: []
""".strip(),
        encoding="utf-8",
    )
    with pytest.raises(CorpusValidationError, match="Invalid ISO date"):
        load_corpus(p)
