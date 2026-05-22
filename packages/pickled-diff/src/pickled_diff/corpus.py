"""Input corpus types."""

from __future__ import annotations

from collections.abc import Iterable, Iterator
from dataclasses import dataclass
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class CorpusItem:
    """One input in a corpus, with a human-readable name."""

    name: str
    payload: str


@runtime_checkable
class Corpus(Protocol):
    """An iterable of CorpusItem with optional length."""

    def __iter__(self) -> Iterator[CorpusItem]: ...

    def __len__(self) -> int: ...


class InMemoryCorpus:
    """A Corpus backed by an in-memory list."""

    _pickled_diff_corpus: bool = True

    def __init__(self, items: Iterable[CorpusItem]) -> None:
        self._items = tuple(items)

    def __iter__(self) -> Iterator[CorpusItem]:
        return iter(self._items)

    def __len__(self) -> int:
        return len(self._items)


__all__ = ["Corpus", "CorpusItem", "InMemoryCorpus"]
