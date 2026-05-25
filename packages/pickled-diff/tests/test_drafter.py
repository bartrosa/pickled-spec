"""Tests for :class:`pickled_diff.drafter.CorpusDrafter`."""

from __future__ import annotations

import json

from pickled_bdd.testing import CannedLLMClient
from pickled_diff.drafter import RATIONALE_SENTINEL, CorpusDrafter

_VALID_CORPUS = json.dumps(
    [
        {"name": "empty", "payload": ""},
        {"name": "one", "payload": "1"},
        {"name": "two", "payload": "2"},
    ]
)


def _with_rationale(body: str, rationale: str = "Expanded seeds.") -> str:
    return f"{body}\n{RATIONALE_SENTINEL}\n{rationale}"


def test_drafts_valid_json_corpus() -> None:
    llm = CannedLLMClient(_with_rationale(_VALID_CORPUS))
    result = CorpusDrafter(llm).draft_from_examples(
        seed_examples=[{"name": "empty", "payload": ""}],
        target_size=3,
    )
    assert len(result.items) == 3
    assert result.warnings == ()
    assert result.rationale == "Expanded seeds."


def test_warns_on_invalid_json() -> None:
    llm = CannedLLMClient(_with_rationale("not json"))
    result = CorpusDrafter(llm).draft_from_examples(
        seed_examples=[],
        target_size=2,
    )
    assert result.items == ()
    assert len(result.warnings) >= 1


def test_warns_on_missing_fields() -> None:
    bad = json.dumps([{"name": "x"}, {"payload": "y"}])
    llm = CannedLLMClient(_with_rationale(bad))
    result = CorpusDrafter(llm).draft_from_examples(
        seed_examples=[],
        target_size=2,
    )
    assert len(result.warnings) >= 1


def test_warns_on_size_mismatch() -> None:
    llm = CannedLLMClient(_with_rationale(_VALID_CORPUS))
    result = CorpusDrafter(llm).draft_from_examples(
        seed_examples=[],
        target_size=5,
    )
    assert any("expected 5" in w for w in result.warnings)


def test_handles_missing_rationale_sentinel() -> None:
    llm = CannedLLMClient(_VALID_CORPUS)
    result = CorpusDrafter(llm).draft_from_examples(
        seed_examples=[],
        target_size=3,
    )
    assert result.rationale == ""
    assert len(result.items) == 3
