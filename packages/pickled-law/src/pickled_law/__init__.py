"""pickled-law: regulatory corpus loading and compliance gates."""

from pickled_law.builtin import BUILTIN_CORPORA, resolve_corpus_name
from pickled_law.corpus import CorpusValidationError, load_corpus
from pickled_law.types import Corpus, CorpusRule, RuleRelation

__all__ = [
    "BUILTIN_CORPORA",
    "Corpus",
    "CorpusRule",
    "CorpusValidationError",
    "RuleRelation",
    "load_corpus",
    "resolve_corpus_name",
]
