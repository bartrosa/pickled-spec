"""Coverage gate: which corpus rules have no citation in the feature?"""

from __future__ import annotations

from dataclasses import dataclass

from pickled_core import Citation, Feature, GateResult, Trace, Verdict

from pickled_law.citations import extract_citations
from pickled_law.types import Corpus, CorpusRule


@dataclass(frozen=True, slots=True)
class CoverageReport:
    cited_rules: tuple[CorpusRule, ...]
    uncited_rules: tuple[CorpusRule, ...]
    unknown_citations: tuple[tuple[str, str], ...]
    """Tags pointing at rule IDs not present in the corpus."""
    gate_result: GateResult


def coverage_gate(
    feature: Feature,
    corpus: Corpus,
    *,
    corpus_short_name: str,
) -> CoverageReport:
    """Compute coverage of ``corpus`` rules by ``feature`` scenarios.

    A rule counts as cited if at least one scenario carries a tag
    ``@<corpus_short_name>:<rule_id>`` (normalized without ``@`` in the model).

    The gate **passes** iff every **required** rule is cited and there are no
    unknown citation tags. **Addressable** rules may remain uncited without
    failing (HIPAA-style semantics).
    """
    scenario_cites = extract_citations(feature, corpus_filter=corpus_short_name)

    cited_ids: set[str] = set()
    unknown: set[tuple[str, str]] = set()
    for sc in scenario_cites:
        for _corpus_name, rule_id in sc.citations:
            if corpus.find(rule_id) is None:
                unknown.add((_corpus_name, rule_id))
            else:
                cited_ids.add(rule_id)

    cited = tuple(r for r in corpus.rules if r.id in cited_ids)
    uncited = tuple(r for r in corpus.rules if r.id not in cited_ids)

    required_uncited = [r for r in uncited if r.obligation == "required"]
    passed = not required_uncited and not unknown

    artifact_ref = feature.path if feature.path else "<feature>"
    traces = tuple(
        Trace(
            citation=Citation(
                source_id=f"{corpus.source_id}({rule.id})",
                source_version=corpus.source_version,
                locator=rule.id,
                canonical_text=rule.text,
                effective_from=corpus.effective_from,
                jurisdiction=corpus.jurisdiction,
                source_url=corpus.source_url,
            ),
            artifact_kind="feature",
            artifact_ref=artifact_ref,
            relation="implements",
            confidence="asserted",
        )
        for rule in cited
    )

    if passed:
        notes = (
            f"All required rules in {corpus.source_id} are cited; "
            "no unknown citation tags."
        )
    else:
        parts: list[str] = []
        if required_uncited:
            parts.append(f"{len(required_uncited)} required rule(s) uncited")
        if unknown:
            parts.append(f"{len(unknown)} unknown citation(s)")
        notes = "; ".join(parts) + "."

    gate_result = GateResult(
        gate_name="law.coverage",
        verdict=Verdict.PASS if passed else Verdict.FAIL,
        findings=(),
        notes=notes,
        traces=traces,
    )

    return CoverageReport(
        cited_rules=cited,
        uncited_rules=uncited,
        unknown_citations=tuple(sorted(unknown)),
        gate_result=gate_result,
    )
