"""Domain types shared across pickled-* packages.

These are runner-agnostic. Packages refine or wrap them as needed; the core
deliberately avoids generics so the types stay simple to import and inspect.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum


class Verdict(StrEnum):
    """Outcome of a gate."""

    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


@dataclass(frozen=True)
class Scenario:
    """A parsed Gherkin scenario, normalized.

    `pickled-bdd` constructs these. Other packages may produce analogous
    units (e.g. an OpenAPI endpoint) under different names.
    """

    name: str
    steps: tuple[str, ...]
    tags: tuple[str, ...] = ()
    line: int = 0


@dataclass(frozen=True)
class Feature:
    """A parsed `.feature` file."""

    name: str
    description: str
    scenarios: tuple[Scenario, ...]
    path: str | None = None


@dataclass(frozen=True)
class AmbiguityFinding:
    """One scenario or artifact that admits multiple implementations."""

    target_name: str
    alternatives: tuple[str, ...]
    suggested_fix: str


@dataclass(frozen=True)
class DraftResult:
    """Output of an LLM-driven drafter."""

    text: str
    rationale: str
    warnings: tuple[str, ...] = ()


@dataclass(frozen=True)
class GateResult:
    """Result of running a compensating gate."""

    gate_name: str
    verdict: Verdict
    findings: tuple[object, ...] = field(default_factory=tuple)
    notes: str = ""
