"""Smoke tests for the bundled HIPAA §164.312 corpus."""

from __future__ import annotations

import pytest
from pickled_law import BUILTIN_CORPORA, load_corpus, resolve_corpus_name


def test_hipaa_corpus_loads() -> None:
    corpus = load_corpus(BUILTIN_CORPORA["hipaa-164.312"])
    assert corpus.source_id == "HIPAA-164.312"
    assert corpus.jurisdiction == "US"
    # 12 rules total: 5 standards + 7 implementation specifications.
    assert len(corpus.rules) == 12


def test_hipaa_corpus_has_expected_standards() -> None:
    corpus = load_corpus(BUILTIN_CORPORA["hipaa-164.312"])
    standard_ids = {r.id for r in corpus.rules if r.parent is None}
    expected = {"(a)(1)", "(b)", "(c)(1)", "(d)", "(e)(1)"}
    assert standard_ids == expected


def test_hipaa_corpus_specs_have_parents() -> None:
    corpus = load_corpus(BUILTIN_CORPORA["hipaa-164.312"])
    specs = [r for r in corpus.rules if r.parent is not None]
    for spec in specs:
        assert corpus.find(spec.parent) is not None, (
            f"spec {spec.id} references missing parent {spec.parent}"
        )


def test_hipaa_alias_resolves() -> None:
    assert resolve_corpus_name("hipaa") == resolve_corpus_name("hipaa-164.312")


def test_unknown_corpus_raises() -> None:
    with pytest.raises(KeyError, match="hipaa-privacy"):
        resolve_corpus_name("hipaa-privacy")
