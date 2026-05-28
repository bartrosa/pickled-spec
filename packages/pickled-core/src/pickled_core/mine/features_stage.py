"""Stage 3: draft Gherkin features from user stories."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

from pickled_core.llm.base import LLMClient
from pickled_core.mine.io import ensure_output_dir, require_stories_dir, surface_matches
from pickled_core.mine.types import FeatureResult, FeaturesStageResult

try:
    from pickled_bdd.drafter import FeatureDrafter
except ImportError:  # pragma: no cover - optional extra
    FeatureDrafter = None  # type: ignore[misc, assignment]  # optional extra not installed


def _story_surface_id(path: Path) -> str:
    name = path.name
    if name.endswith(".story.md"):
        return name[: -len(".story.md")]
    return path.stem


def _package_from_story(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    for line in text.splitlines():
        if line.startswith("- **Package:**"):
            return line.split(":**", 1)[-1].strip()
    surface_id = _story_surface_id(path)
    return surface_id.split("_", 1)[0] if "_" in surface_id else surface_id


def _filter_story_paths(
    story_paths: list[Path],
    surfaces: tuple[str, ...],
) -> list[Path]:
    if not surfaces:
        return story_paths
    filtered: list[Path] = []
    for story_path in story_paths:
        surface_id = _story_surface_id(story_path)
        package = _package_from_story(story_path)
        if surface_matches(surface_id=surface_id, package=package, tokens=surfaces):
            filtered.append(story_path)
    return filtered


async def _draft_one(
    story_path: Path,
    feature_path: Path,
    llm: LLMClient,
    *,
    overwrite: bool,
    interactive: bool,
) -> FeatureResult:
    surface_id = _story_surface_id(story_path)
    if feature_path.is_file() and not overwrite:
        return FeatureResult(
            surface_id=surface_id,
            feature_path=feature_path,
            story_path=story_path,
            skipped=True,
        )

    if FeatureDrafter is None:
        msg = "pickled-bdd is not installed; install pickled-core[mine]"
        raise RuntimeError(msg)

    story_text = story_path.read_text(encoding="utf-8")
    drafter = FeatureDrafter(llm)

    while True:
        result = drafter.draft_from_story(story_text)
        feature_text = result.text
        if not interactive:
            feature_path.write_text(feature_text + "\n", encoding="utf-8")
            return FeatureResult(
                surface_id=surface_id,
                feature_path=feature_path,
                story_path=story_path,
                skipped=False,
            )

        sys.stderr.write(f"\n--- draft for {surface_id} ---\n")
        sys.stderr.write(feature_text[:2000])
        if len(feature_text) > 2000:
            sys.stderr.write("\n…\n")
        sys.stderr.write("\n")
        choice = input("accept / skip / re-draft: ").strip().lower()
        if choice == "skip":
            return FeatureResult(
                surface_id=surface_id,
                feature_path=feature_path,
                story_path=story_path,
                skipped=True,
            )
        if choice in {"accept", "a", "y", "yes"}:
            feature_path.write_text(feature_text + "\n", encoding="utf-8")
            return FeatureResult(
                surface_id=surface_id,
                feature_path=feature_path,
                story_path=story_path,
                skipped=False,
            )
        if choice in {"re-draft", "redraft", "r"}:
            continue
        sys.stderr.write("Unknown choice; type accept, skip, or re-draft.\n")


async def _run_parallel(
    jobs: list[tuple[Path, Path]],
    llm: LLMClient,
    *,
    overwrite: bool,
    max_parallel: int,
) -> list[FeatureResult]:
    sem = asyncio.Semaphore(max_parallel)
    results: list[FeatureResult] = []

    async def _one(story_path: Path, feature_path: Path) -> None:
        async with sem:
            results.append(
                await _draft_one(
                    story_path,
                    feature_path,
                    llm,
                    overwrite=overwrite,
                    interactive=False,
                )
            )

    await asyncio.gather(*[_one(s, f) for s, f in jobs])
    return sorted(results, key=lambda r: r.surface_id)


def run_features(
    output_dir: Path,
    *,
    llm: LLMClient | None,
    quick: bool,
    overwrite: bool,
    surfaces: tuple[str, ...] = (),
    max_parallel: int = 4,
) -> FeaturesStageResult:
    """Draft ``.feature`` files from stories under ``output_dir``."""
    paths = ensure_output_dir(output_dir)
    stories_dir = require_stories_dir(output_dir, needed_by="features")

    if llm is None:
        sys.stderr.write("[WARN] features stage requires an LLM; skipped\n")
        return FeaturesStageResult(
            output_dir=paths.root,
            results=[],
            skipped_entire_stage=True,
            warnings=["features stage requires an LLM; skipped"],
        )

    story_paths = _filter_story_paths(
        sorted(stories_dir.glob("*.story.md")),
        surfaces,
    )
    if not story_paths:
        msg = "no stories match --surfaces filter"
        raise ValueError(msg)

    jobs = [
        (
            story_path,
            paths.features_dir / f"{_story_surface_id(story_path)}.feature",
        )
        for story_path in story_paths
    ]

    if quick:
        results = asyncio.run(
            _run_parallel(jobs, llm, overwrite=overwrite, max_parallel=max_parallel)
        )
    else:
        results = []
        for story_path, feature_path in jobs:
            results.append(
                asyncio.run(
                    _draft_one(
                        story_path,
                        feature_path,
                        llm,
                        overwrite=overwrite,
                        interactive=True,
                    )
                )
            )

    return FeaturesStageResult(output_dir=paths.root, results=results, skipped_entire_stage=False)


__all__ = ["run_features"]
