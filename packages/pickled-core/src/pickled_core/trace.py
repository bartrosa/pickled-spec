"""Traceability primitives shared across the pickled-* family.

A `Citation` is a pointer to a source artifact (regulation, user story,
internal SOP) with enough metadata to detect drift. A `Trace` links a
citation to a target artifact (feature file, scenario, test, function)
and describes the relationship.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Literal

ArtifactKind = Literal["feature", "scenario", "test", "function", "data_flow"]
Relation = Literal["implements", "constrains", "exempts", "supersedes"]
Confidence = Literal["asserted", "verified", "drift_suspected"]


@dataclass(frozen=True, slots=True)
class Citation:
    """Pointer to a source artifact with version pinning."""

    source_id: str
    """Stable identifier of the source corpus item.

    Examples: "HIPAA-164.312(a)(2)(i)", "RODO-Art-32-ust-1",
    "MDR-Annex-I-17.2", "INTERNAL-SOP-AUTH-001".
    """

    source_version: str
    """Version of the source that this citation pins to.

    Regulations: rule date or amendment ID. Internal docs: git ref or
    semantic version. Required because regulations change and traces
    must be invalidated when they do.
    """

    locator: str
    """Sub-locator within the source.

    Examples: "(a)(2)(iii)", "section 4.3.1", "ust. 1 lit. f".
    """

    canonical_text: str
    """The actual text of the cited clause, copied verbatim.

    This lets gates compare against the live source and detect drift
    even when ids are stable but wording changed.
    """

    effective_from: date
    """Date this version of the citation became binding."""

    jurisdiction: str
    """ISO country code or supranational identifier.

    Examples: "US", "EU", "PL", "global" (for ISO/IEC standards),
    "internal" (for company-internal sources).
    """

    effective_until: date | None = None
    """Date this version stops being binding. None = currently in force."""

    source_url: str | None = None
    """Optional canonical URL for human review."""


@dataclass(frozen=True, slots=True)
class Trace:
    """Link between a `Citation` and a project artifact."""

    citation: Citation
    artifact_kind: ArtifactKind
    artifact_ref: str
    """Path or fully-qualified name of the artifact.

    Examples: "features/auth.feature", "features/auth.feature::login",
    "src/auth/session.py::auto_logoff".
    """

    relation: Relation
    confidence: Confidence
