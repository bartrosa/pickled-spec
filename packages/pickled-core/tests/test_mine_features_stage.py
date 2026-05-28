"""Tests for mine features stage."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from pickled_core import DraftResult
from pickled_core.mine.errors import MissingStageInputError
from pickled_core.mine.features_stage import run_features
from pickled_core.mine.stories_stage import run_stories

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"


def test_run_features_skipped_without_llm(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    run_stories(inv, tmp_path, llm=None, quick=True, overwrite=True)
    result = run_features(tmp_path, llm=None, quick=True, overwrite=True)
    assert result.skipped_entire_stage
    assert not list((tmp_path / "features").glob("*.feature"))


def test_run_features_drafts_with_llm(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    run_stories(inv, tmp_path, llm=None, quick=True, overwrite=True)

    class _FakeDrafter:
        def __init__(self, llm: Any) -> None:
            _ = llm

        def draft_from_story(self, story: str) -> DraftResult:
            return DraftResult(
                text="Feature: tiny\n\n  Scenario: ok\n    Given x\n",
                rationale="test",
                warnings=(),
            )

    monkeypatch.setattr("pickled_core.mine.features_stage.FeatureDrafter", _FakeDrafter)

    class _Client:
        pass

    result = run_features(tmp_path, llm=_Client(), quick=True, overwrite=True)  # type: ignore[arg-type]
    assert not result.skipped_entire_stage
    assert result.results
    assert result.results[0].feature_path.is_file()


def test_run_features_requires_stories(tmp_path: Path) -> None:
    with pytest.raises(MissingStageInputError, match="mine stories"):
        run_features(tmp_path, llm=None, quick=True, overwrite=True)


def test_features_respects_surfaces_filter(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    stories = tmp_path / "stories"
    stories.mkdir()
    (stories / "tiny_target_greet.story.md").write_text("# Story\n", encoding="utf-8")
    (stories / "other_pkg_ping.story.md").write_text("# Story\n", encoding="utf-8")

    class _FakeDrafter:
        def __init__(self, llm: Any) -> None:
            _ = llm

        def draft_from_story(self, story: str) -> DraftResult:
            return DraftResult(
                text=f"Feature: x\n\n  Scenario: from {story[:20]}\n    Given y\n",
                rationale="test",
                warnings=(),
            )

    monkeypatch.setattr("pickled_core.mine.features_stage.FeatureDrafter", _FakeDrafter)

    class _Client:
        pass

    result = run_features(
        tmp_path,
        llm=_Client(),  # type: ignore[arg-type]
        quick=True,
        overwrite=True,
        surfaces=("greet",),
    )
    assert not result.skipped_entire_stage
    assert len(result.results) == 1
    assert result.results[0].surface_id == "tiny_target_greet"
