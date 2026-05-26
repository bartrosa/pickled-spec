"""Read/write helpers for mining output directories."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pickled_core.mine.types import MiningPaths


def ensure_output_dir(output_dir: Path) -> MiningPaths:
    """Create the mining output tree if missing."""
    paths = MiningPaths(output_dir.resolve())
    paths.root.mkdir(parents=True, exist_ok=True)
    paths.stories_dir.mkdir(parents=True, exist_ok=True)
    paths.features_dir.mkdir(parents=True, exist_ok=True)
    paths.evaluation_dir.mkdir(parents=True, exist_ok=True)
    paths.runs_dir.mkdir(parents=True, exist_ok=True)
    return paths


def read_json(path: Path) -> Any:
    if not path.is_file():
        msg = f"required input missing: {path}"
        raise FileNotFoundError(msg)
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def read_json_optional(path: Path) -> Any | None:
    if not path.is_file():
        return None
    return read_json(path)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


__all__ = ["ensure_output_dir", "read_json", "read_json_optional", "write_json", "write_text"]
