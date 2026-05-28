"""Shared types for the mining pipeline."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from pickled_rules.types import RuleSet


@dataclass
class InventoryResult:
    """Result of the inventory stage."""

    inventory_path: Path
    data: dict[str, Any]
    warnings: list[str] = field(default_factory=list)


@dataclass
class StageResult:
    """Generic stage completion metadata."""

    stage: str
    output_dir: Path
    warnings: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0


@dataclass
class MiningPaths:
    """Canonical paths under a mining output directory."""

    root: Path

    @property
    def inventory_json(self) -> Path:
        return self.root / "inventory.json"

    @property
    def stories_dir(self) -> Path:
        return self.root / "stories"

    @property
    def features_dir(self) -> Path:
        return self.root / "features"

    @property
    def tags_proposals(self) -> Path:
        return self.root / "tags-proposals.json"

    @property
    def evaluation_dir(self) -> Path:
        return self.root / "evaluation"

    @property
    def coverage_json(self) -> Path:
        return self.evaluation_dir / "coverage.json"

    @property
    def ambiguity_json(self) -> Path:
        return self.evaluation_dir / "ambiguity.json"

    @property
    def mining_report(self) -> Path:
        return self.root / "mining-report.md"

    @property
    def runs_dir(self) -> Path:
        return self.root / "runs"

    @property
    def code_context_dir(self) -> Path:
        return self.root / "code-context"


ResolutionKind = Literal[
    "free_function",
    "self_method",
    "constructor_method",
    "annotated_var",
    "annotated_param",
    "assigned_constructor",
    "module_constructor",
    "unresolved",
]


@dataclass(frozen=True, slots=True)
class CalleeRef:
    """Callee edge recorded during code reading (serializable subset)."""

    expression: str
    name: str
    module: str
    file: str
    lineno: int
    resolved: bool
    reason: str = ""
    key: str = ""
    resolution_kind: str = "unresolved"


@dataclass
class CodeContext:
    """Aggregate code units collected for one surface."""

    surface_id: str
    depth: str
    scope: str
    units_collected: int
    total_lines: int
    truncated: bool
    no_definition: bool
    context_path: Path | None = None


@dataclass
class CycleReport:
    """Cycle detection output for code reading."""

    cycles: list[list[str]] = field(default_factory=list)

    @property
    def count(self) -> int:
        return len(self.cycles)


@dataclass
class CodeStageResult:
    """Result of the code reading stage."""

    output_dir: Path
    code_context_dir: Path
    written_paths: list[Path] = field(default_factory=list)
    cycles_path: Path | None = None
    cycle_count: int = 0


@dataclass
class RelevantAdrRef:
    """ADR entry attached to a mined surface."""

    number: str
    title: str
    status: str
    general: bool = False


@dataclass
class MinedSurfaceContext:
    """Per-surface fields used when rendering stories."""

    docstring: str = ""
    relevant_adrs: list[RelevantAdrRef] = field(default_factory=list)


@dataclass
class StoryResult:
    """One emitted user story file."""

    surface_id: str
    story_path: Path
    skipped: bool = False


@dataclass
class FeatureResult:
    """One drafted feature file."""

    surface_id: str
    feature_path: Path
    story_path: Path
    skipped: bool = False


@dataclass
class FeaturesStageResult:
    """Aggregate result of the features stage."""

    output_dir: Path
    results: list[FeatureResult] = field(default_factory=list)
    skipped_entire_stage: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class TagProposal:
    """A single proposed scenario tag."""

    tag: str
    rule_id: str
    short_name: str
    rule_title: str
    score: int


@dataclass
class LoadedRulesetEntry:
    """One rule set file loaded for tagging."""

    short_name: str
    path: Path
    ruleset: RuleSet


@dataclass
class RulesetSources:
    """Loaded rule sets for tagging."""

    config_root: Path
    rulesets: list[LoadedRulesetEntry] = field(default_factory=list)


@dataclass
class TagResult:
    """Result of the tag stage."""

    proposals_path: Path
    proposals: list[Any] = field(default_factory=list)
    skipped: bool = False
    warnings: list[str] = field(default_factory=list)


@dataclass
class CoverageRulesetResult:
    """Coverage gate outcome for one rule set."""

    short_name: str
    verdict: str
    notes: str
    referenced_rule_ids: list[str] = field(default_factory=list)
    unreferenced_strict_rule_ids: list[str] = field(default_factory=list)
    unknown_references: list[dict[str, str]] = field(default_factory=list)


@dataclass
class AmbiguityFeatureResult:
    """Ambiguity gate outcome for one feature file."""

    feature_path: str
    verdict: str
    finding_count: int
    skipped: bool
    notes: str


@dataclass
class EvaluationResult:
    """Result of the evaluate stage."""

    coverage_path: Path
    ambiguity_path: Path
    coverage: list[CoverageRulesetResult] = field(default_factory=list)
    ambiguity: list[AmbiguityFeatureResult] = field(default_factory=list)
    surfaces_filter: tuple[str, ...] = ()


__all__ = [
    "AmbiguityFeatureResult",
    "CalleeRef",
    "CodeContext",
    "CodeStageResult",
    "CoverageRulesetResult",
    "CycleReport",
    "EvaluationResult",
    "FeatureResult",
    "FeaturesStageResult",
    "InventoryResult",
    "LoadedRulesetEntry",
    "MinedSurfaceContext",
    "MiningPaths",
    "ResolutionKind",
    "RelevantAdrRef",
    "RulesetSources",
    "StageResult",
    "StoryResult",
    "TagProposal",
    "TagResult",
]
