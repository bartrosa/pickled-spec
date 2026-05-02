"""pickled-law: regulatory corpus loading and compliance gates."""

from pickled_law.builtin import BUILTIN_CORPORA, resolve_corpus_name
from pickled_law.citations import ScenarioCitations, extract_citations
from pickled_law.corpus import CorpusValidationError, load_corpus
from pickled_law.gates import CoverageReport, coverage_gate
from pickled_law.rtm import render_rtm_markdown
from pickled_law.types import Corpus, CorpusRule, RuleRelation

__all__ = [
    "BUILTIN_CORPORA",
    "Corpus",
    "CorpusRule",
    "CorpusValidationError",
    "CoverageReport",
    "RuleRelation",
    "ScenarioCitations",
    "coverage_gate",
    "extract_citations",
    "load_corpus",
    "render_rtm_markdown",
    "resolve_corpus_name",
]
