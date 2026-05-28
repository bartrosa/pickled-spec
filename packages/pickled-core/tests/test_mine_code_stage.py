"""Tests for mine code stage."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from pickled_core.mine.code_stage import run_code
from pickled_core.mine.errors import MissingStageInputError
from pickled_core.mine.inventory_stage import run_inventory
from pickled_core.mine.types import InventoryResult

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "callgraph_target"


def test_writes_code_context_per_surface(tmp_path: Path) -> None:
    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    result = run_code(
        inv,
        _FIXTURE,
        tmp_path,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        verbose=False,
    )
    assert result.code_context_dir.is_dir()
    md_files = list(result.code_context_dir.glob("*.md"))
    assert md_files
    text = md_files[0].read_text(encoding="utf-8")
    assert "# Code context:" in text


def test_respects_surfaces_filter(tmp_path: Path) -> None:
    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    result = run_code(
        inv,
        _FIXTURE,
        tmp_path,
        surfaces=("chain",),
        verbose=False,
    )
    names = {p.stem for p in result.written_paths}
    assert names
    assert all("chain" in n or "entry" in n for n in names)


def test_missing_inventory_raises_actionable_error(tmp_path: Path) -> None:
    from pickled_core.mine.code_stage import load_inventory_for_code

    with pytest.raises(MissingStageInputError) as exc:
        load_inventory_for_code(tmp_path)
    assert "mine inventory" in str(exc.value)


def test_cycles_json_written_when_detect_enabled(tmp_path: Path) -> None:
    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    result = run_code(
        inv,
        _FIXTURE,
        tmp_path,
        depth="callgraph",
        max_hops=2,
        detect_cycles=True,
        verbose=False,
    )
    assert result.cycles_path is not None
    assert result.cycles_path.is_file()
    payload = json.loads(result.cycles_path.read_text(encoding="utf-8"))
    assert "cycles" in payload
    assert payload["count"] >= 0


def test_no_cycles_json_when_disabled(tmp_path: Path) -> None:
    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    result = run_code(
        inv,
        _FIXTURE,
        tmp_path,
        detect_cycles=False,
        verbose=False,
    )
    assert result.cycles_path is None


def test_surface_without_code_definition_writes_placeholder(tmp_path: Path) -> None:
    data = {
        "packages": {
            "demo": {
                "cli_commands": [],
                "mcp_tools": [{"name": "orphan_tool", "description": "x"}],
                "gates": [],
                "scripts": {},
            }
        }
    }
    inv = InventoryResult(
        inventory_path=tmp_path / "inventory.json",
        data=data,
    )
    result = run_code(inv, _FIXTURE, tmp_path, verbose=False)
    orphan = result.code_context_dir / "orphan_tool.md"
    assert orphan.is_file()
    assert "No code definition resolved" in orphan.read_text(encoding="utf-8")


def test_truncation_note_present_when_capped(tmp_path: Path) -> None:
    from pickled_core.mine.code_reader import SurfaceRef, collect_context
    from pickled_core.mine.code_stage import _render_code_context_markdown

    surface = SurfaceRef(
        surface_id="cg_entry",
        kind="function",
        package="callgraph-target",
        name="entry",
        module="callgraph_target",
        file="packages/callgraph_target/src/callgraph_target/fanout.py",
        line=40,
    )
    ctx = collect_context(
        surface,
        _FIXTURE,
        depth="callgraph",
        scope="same-package",
        max_hops=1,
        max_callees=20,
        max_code_lines=3,
        package="callgraph-target",
    )
    text = _render_code_context_markdown(ctx, max_hops=1)
    assert ctx.truncated
    assert "max-code-lines" in text
