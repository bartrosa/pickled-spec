"""pickled-rules: rule coverage analysis for project artifacts."""

from pickled_rules.builtin import BUILTIN_RULESETS, resolve_ruleset_name
from pickled_rules.gates import CoverageReport, coverage_gate
from pickled_rules.loader import RuleSetValidationError, load_ruleset
from pickled_rules.references import ScenarioReferences, extract_references
from pickled_rules.report import render_coverage_json, render_coverage_markdown
from pickled_rules.types import Enforcement, Rule, RuleRelation, RuleSet

__all__ = [
    "BUILTIN_RULESETS",
    "CoverageReport",
    "Enforcement",
    "Rule",
    "RuleRelation",
    "RuleSet",
    "RuleSetValidationError",
    "ScenarioReferences",
    "coverage_gate",
    "extract_references",
    "load_ruleset",
    "render_coverage_json",
    "render_coverage_markdown",
    "resolve_ruleset_name",
]
