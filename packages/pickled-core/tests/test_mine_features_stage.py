"""Tests for mine features stage."""

from __future__ import annotations

import threading
import time
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


def test_max_parallel_actually_overlaps_llm_calls(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """`--max-parallel N` must let up to N LLM drafts run concurrently.

    Regression for a bug where ``_draft_one`` was an ``async def`` that
    invoked the synchronous ``FeatureDrafter.draft_from_story`` directly:
    every coroutine blocked the event loop for the entire LLM call, so
    the asyncio.Semaphore never released to a waiting task and the
    advertised ``--max-parallel`` flag silently degraded to 1-way
    serial execution. With 50 surfaces × 5s LLM calls, that turns a
    ~63 s mining run with ``--max-parallel 8`` into ~250 s.
    """
    stories = tmp_path / "stories"
    stories.mkdir()
    for index in range(8):
        (stories / f"surf_{index}.story.md").write_text("# story\n", encoding="utf-8")

    state: dict[str, int] = {"current": 0, "peak": 0}
    lock = threading.Lock()

    class _SlowDrafter:
        def __init__(self, llm: Any) -> None:
            _ = llm

        def draft_from_story(self, story: str) -> DraftResult:
            _ = story
            with lock:
                state["current"] += 1
                if state["current"] > state["peak"]:
                    state["peak"] = state["current"]
            try:
                time.sleep(0.2)
            finally:
                with lock:
                    state["current"] -= 1
            return DraftResult(
                text="Feature: x\n\n  Scenario: y\n    Given z\n",
                rationale="",
                warnings=(),
            )

    monkeypatch.setattr("pickled_core.mine.features_stage.FeatureDrafter", _SlowDrafter)

    class _Client:
        pass

    started = time.time()
    result = run_features(
        tmp_path,
        llm=_Client(),  # type: ignore[arg-type]
        quick=True,
        overwrite=True,
        max_parallel=4,
    )
    elapsed = time.time() - started

    assert len(result.results) == 8
    # 4-way parallelism over 8 jobs of 0.2s each: ideal ~0.4s, accept up to 1.5s
    # for slow CI jitter; serial would take ~1.6s and we want a clear gap.
    assert state["peak"] >= 2, (
        f"max-parallel=4 should overlap LLM calls; observed peak={state['peak']}"
    )
    assert elapsed < 1.5, f"max-parallel=4 should run in well under serial time; got {elapsed:.2f}s"
