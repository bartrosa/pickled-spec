"""Coverage gate: which rule-set rules have no reference in the feature?"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

from pickled_core import Feature, GateResult, SourceReference, Trace, Verdict

from pickled_rules.references import extract_references
from pickled_rules.types import Rule, RuleSet


@dataclass(frozen=True, slots=True)
class CoverageReport:
    referenced_rules: tuple[Rule, ...]
    unreferenced_rules: tuple[Rule, ...]
    unknown_references: tuple[tuple[str, str], ...]
    """Tags pointing at rule IDs not present in the rule set."""
    gate_result: GateResult


def _collect_references(
    features: Sequence[Feature],
    ruleset: RuleSet,
    *,
    ruleset_short_name: str,
) -> tuple[set[str], set[tuple[str, str]]]:
    referenced_ids: set[str] = set()
    unknown: set[tuple[str, str]] = set()
    for feature in features:
        scenario_refs = extract_references(feature, ruleset_filter=ruleset_short_name)
        for sc in scenario_refs:
            for _ruleset_name, rule_id in sc.references:
                if ruleset.find(rule_id) is None:
                    unknown.add((_ruleset_name, rule_id))
                else:
                    referenced_ids.add(rule_id)
    return referenced_ids, unknown


def coverage_gate(
    feature: Feature,
    ruleset: RuleSet,
    *,
    ruleset_short_name: str,
) -> CoverageReport:
    """Compute coverage of ``ruleset`` rules by ``feature`` scenarios.

    A rule counts as referenced if at least one scenario carries a tag
    ``@<ruleset_short_name>:<rule_id>`` (normalized without ``@`` in the model).

    The gate **passes** iff every **strict** rule is referenced and there are no
    unknown reference tags. **Advisory** and **informational** rules may remain
    unreferenced without failing.
    """
    return coverage_gate_features(
        (feature,),
        ruleset,
        ruleset_short_name=ruleset_short_name,
        artifact_ref=feature.path if feature.path else "<feature>",
    )


def coverage_gate_features(
    features: Sequence[Feature],
    ruleset: RuleSet,
    *,
    ruleset_short_name: str,
    artifact_ref: str | None = None,
) -> CoverageReport:
    """Compute coverage across one or more features (union of scenario tags)."""
    referenced_ids, unknown = _collect_references(
        features, ruleset, ruleset_short_name=ruleset_short_name
    )
    if artifact_ref is None:
        paths = [f.path for f in features if f.path]
        artifact_ref = ", ".join(paths) if paths else "<features>"

    referenced = tuple(r for r in ruleset.rules if r.id in referenced_ids)
    unreferenced = tuple(r for r in ruleset.rules if r.id not in referenced_ids)

    strict_unreferenced = [r for r in unreferenced if r.enforcement == "strict"]
    passed = not strict_unreferenced and not unknown

    traces = tuple(
        Trace(
            source_reference=SourceReference(
                source_id=f"{ruleset.source_id}({rule.id})",
                source_version=ruleset.source_version,
                locator=rule.id,
                description=rule.description,
                active_from=ruleset.active_from,
                applies_to=ruleset.applies_to,
                source_url=ruleset.source_url,
            ),
            artifact_kind="feature",
            artifact_ref=artifact_ref,
            relation="implements",
            confidence="asserted",
        )
        for rule in referenced
    )

    if passed:
        notes = (
            f"All strict rules in {ruleset.source_id} are referenced; no unknown reference tags."
        )
    else:
        parts: list[str] = []
        if strict_unreferenced:
            parts.append(f"{len(strict_unreferenced)} strict rule(s) unreferenced")
        if unknown:
            parts.append(f"{len(unknown)} unknown reference(s)")
        notes = "; ".join(parts) + "."

    gate_result = GateResult(
        gate_name="rules.coverage",
        verdict=Verdict.PASS if passed else Verdict.FAIL,
        findings=(),
        notes=notes,
        traces=traces,
    )

    return CoverageReport(
        referenced_rules=referenced,
        unreferenced_rules=unreferenced,
        unknown_references=tuple(sorted(unknown)),
        gate_result=gate_result,
    )
