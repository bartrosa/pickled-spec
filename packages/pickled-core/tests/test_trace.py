from __future__ import annotations

import dataclasses
from dataclasses import FrozenInstanceError
from datetime import date

import pytest
from pickled_core import SourceReference, Trace


def _sample_reference() -> SourceReference:
    return SourceReference(
        source_id="TEAM-CONV-1",
        source_version="2024.1",
        locator="naming.1",
        description="Endpoints under /v1 must be versioned.",
        active_from=date(2024, 1, 1),
        applies_to="backend",
    )


def test_source_reference_is_frozen() -> None:
    ref = _sample_reference()
    with pytest.raises(FrozenInstanceError):
        ref.source_id = "x"  # type: ignore[misc]


def test_source_reference_is_hashable() -> None:
    a = _sample_reference()
    b = SourceReference(
        source_id="TEAM-CONV-1",
        source_version="2024.1",
        locator="naming.1",
        description="Endpoints under /v1 must be versioned.",
        active_from=date(2024, 1, 1),
        applies_to="backend",
    )
    assert hash(a) == hash(b)
    assert {a, b} == {a}


def test_source_reference_equality() -> None:
    base = _sample_reference()
    assert base == SourceReference(
        source_id=base.source_id,
        source_version=base.source_version,
        locator=base.locator,
        description=base.description,
        active_from=base.active_from,
        applies_to=base.applies_to,
    )
    assert base != dataclasses.replace(base, source_id="other")
    assert base != dataclasses.replace(base, source_version="x")
    assert base != dataclasses.replace(base, locator="x")
    assert base != dataclasses.replace(base, description="x")
    assert base != dataclasses.replace(base, active_from=date(2000, 1, 1))
    assert base != dataclasses.replace(base, applies_to="frontend")
    assert base != dataclasses.replace(base, active_until=date(2020, 1, 1))
    assert base != dataclasses.replace(base, source_url="https://example.com")


def test_source_reference_optional_fields() -> None:
    ref = _sample_reference()
    assert ref.active_until is None
    assert ref.source_url is None
    updated = dataclasses.replace(
        ref,
        active_until=date(2025, 1, 1),
        source_url="https://example.com/team-conv",
    )
    assert updated.active_until == date(2025, 1, 1)
    assert updated.source_url == "https://example.com/team-conv"


def test_trace_round_trip_asdict() -> None:
    ref = _sample_reference()
    trace = Trace(
        source_reference=ref,
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
    assert d["source_reference"] == {
        "source_id": ref.source_id,
        "source_version": ref.source_version,
        "locator": ref.locator,
        "description": ref.description,
        "active_from": ref.active_from,
        "applies_to": ref.applies_to,
        "active_until": ref.active_until,
        "source_url": ref.source_url,
    }


def test_trace_invalid_relation_caught_by_mypy() -> None:
    """Runtime cannot enforce Literal types; mypy does at type-check time."""
