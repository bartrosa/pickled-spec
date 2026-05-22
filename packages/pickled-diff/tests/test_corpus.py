from __future__ import annotations

from pickled_diff.corpus import Corpus, CorpusItem, InMemoryCorpus


def test_in_memory_corpus_iterates_in_order() -> None:
    items = [CorpusItem("a", "1"), CorpusItem("b", "2")]
    names = [i.name for i in InMemoryCorpus(items)]
    assert names == ["a", "b"]


def test_in_memory_corpus_length() -> None:
    assert len(InMemoryCorpus([CorpusItem("x", "y")])) == 1


def test_in_memory_corpus_is_corpus_protocol() -> None:
    assert isinstance(InMemoryCorpus([]), Corpus)
