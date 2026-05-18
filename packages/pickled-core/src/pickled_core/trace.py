"""Traceability primitives shared across the pickled-* family.

A `SourceReference` is a pointer to a rule or specification artifact with
enough metadata to detect drift. A `Trace` links a `SourceReference` to a
target project artifact (feature file, scenario, test, function) and
describes the relationship.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

ArtifactKind = Literal["feature", "scenario", "test", "function", "data_flow"]
Relation = Literal["implements", "constrains", "exempts", "supersedes"]
Confidence = Literal["asserted", "verified", "drift_suspected"]


@dataclass(frozen=True, slots=True)
class SourceReference:
    """Pointer to a source artifact with version pinning."""

    source_id: str
    """Stable identifier of the source item.

    Examples: "TEAM-API-CONV-001", "REVIEW-CHK-3", "INTERNAL-STYLE-007".
    """

    source_version: str
    """Version of the source that this reference pins to.

    Internal docs: git ref or semantic version. Required because sources
    change and traces must be invalidated when they do.
    """

    locator: str
    """Sub-locator within the source.

    Examples: "naming.1", "section 4.3.1", "review-3".
    """

    description: str
    """The text of the referenced rule or clause, copied verbatim.

    This lets gates compare against the live source and detect drift
    even when ids are stable but wording changed.
    """

    active_from: date
    """Date this version of the reference became active."""

    applies_to: str
    """Scope label for where the reference applies.

    Examples: "backend-team", "all-services", "frontend", "global".
    """

    active_until: date | None = None
    """Date this version stops being active. None = currently active."""

    source_url: str | None = None
    """Optional canonical URL for human review."""


@dataclass(frozen=True, slots=True)
class Trace:
    """Link between a `SourceReference` and a project artifact."""

    source_reference: SourceReference
    artifact_kind: ArtifactKind
    artifact_ref: str
    """Path or fully-qualified name of the artifact.

    Examples: "features/auth.feature", "features/auth.feature::login",
    "src/auth/session.py::auto_logoff".
    """

    relation: Relation
    confidence: Confidence
