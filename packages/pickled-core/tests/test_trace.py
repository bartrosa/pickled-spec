from __future__ import annotations

import dataclasses
from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from pickled_core import Citation, Trace

# Mypy would flag invalid Literal values at compile time, e.g.:
# Trace(
#     citation=_sample_citation(),
#     artifact_kind="feature",
#     artifact_ref="x",
#     relation="not-a-relation",  # type: ignore[arg-type]
#     confidence="asserted",
# )
# Runtime does not validate Literal; mypy does.


def _sample_citation() -> Citation:
    return Citation(
        source_id="HIPAA-164.312(a)(2)(iii)",
        source_version="2013-omnibus",
        locator="(a)(2)(iii)",
        canonical_text=(
            "Implement electronic procedures that terminate "
            "an electronic session after a predetermined "
            "time of inactivity."
        ),
        effective_from=date(2013, 9, 23),
        jurisdiction="US",
    )


def test_citation_is_frozen() -> None:
    c = _sample_citation()
    with pytest.raises(FrozenInstanceError):
        c.source_id = "x"  # type: ignore[misc]


def test_citation_is_hashable() -> None:
    a = _sample_citation()
    b = Citation(
        source_id="HIPAA-164.312(a)(2)(iii)",
        source_version="2013-omnibus",
        locator="(a)(2)(iii)",
        canonical_text=(
            "Implement electronic procedures that terminate "
            "an electronic session after a predetermined "
            "time of inactivity."
        ),
        effective_from=date(2013, 9, 23),
        jurisdiction="US",
    )
    assert hash(a) == hash(b)
    assert {a, b} == {a}


def test_citation_equality() -> None:
    base = _sample_citation()
    assert base == Citation(
        source_id=base.source_id,
        source_version=base.source_version,
        locator=base.locator,
        canonical_text=base.canonical_text,
        effective_from=base.effective_from,
        jurisdiction=base.jurisdiction,
    )
    assert base != dataclasses.replace(base, source_id="other")
    assert base != dataclasses.replace(base, source_version="x")
    assert base != dataclasses.replace(base, locator="x")
    assert base != dataclasses.replace(base, canonical_text="x")
    assert base != dataclasses.replace(base, effective_from=date(2000, 1, 1))
    assert base != dataclasses.replace(base, jurisdiction="EU")
    assert base != dataclasses.replace(base, effective_until=date(2020, 1, 1))
    assert base != dataclasses.replace(base, source_url="https://example.com")


def test_citation_optional_fields() -> None:
    c = _sample_citation()
    assert c.effective_until is None
    assert c.source_url is None
    d = dataclasses.replace(
        c,
        effective_until=date(2025, 1, 1),
        source_url="https://www.hhs.gov/hipaa",
    )
    assert d.effective_until == date(2025, 1, 1)
    assert d.source_url == "https://www.hhs.gov/hipaa"


def test_trace_round_trip_asdict() -> None:
    citation = _sample_citation()
    trace = Trace(
        citation=citation,
        artifact_kind="scenario",
        artifact_ref="features/auth.feature::login",
        relation="implements",
        confidence="verified",
    )
    d = dataclasses.asdict(trace)
    assert d["artifact_kind"] == "scenario"
    assert d["artifact_ref"] == "features/auth.feature::login"
    assert d["relation"] == "implements"
    assert d["confidence"] == "verified"
    assert d["citation"] == {
        "source_id": citation.source_id,
        "source_version": citation.source_version,
        "locator": citation.locator,
        "canonical_text": citation.canonical_text,
        "effective_from": citation.effective_from,
        "jurisdiction": citation.jurisdiction,
        "effective_until": citation.effective_until,
        "source_url": citation.source_url,
    }


def test_trace_invalid_relation_caught_by_mypy() -> None:
    """Runtime cannot enforce Literal types; mypy does at type-check time."""
