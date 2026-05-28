"""Stage: extract per-surface code context from inventory."""

from __future__ import annotations

import sys
from pathlib import Path

from pickled_core.mine.code_reader import (
    CalleeScope,
    CodeContext,
    CycleReport,
    Depth,
    collect_context,
    find_cycles,
    iter_surfaces_from_inventory,
)
from pickled_core.mine.io import (
    ensure_output_dir,
    require_inventory_json,
    surface_matches,
    write_json,
    write_text,
)
from pickled_core.mine.types import CodeStageResult, InventoryResult


def _render_code_context_markdown(
    ctx: CodeContext,
    *,
    max_hops: int,
) -> str:
    surface = ctx.surface
    lines: list[str] = [
        f"# Code context: {surface.name}",
        "",
        f"- **Surface id:** {surface.surface_id}",
        f"- **Depth:** {ctx.depth} | **Scope:** {ctx.scope} | **Hops:** {max_hops}",
    ]
    total_lines = sum(u.line_count for u in ctx.units)
    lines.append(
        f"- **Units collected:** {len(ctx.units)} | **Total lines:** {total_lines} "
        f"| **Truncated:** {ctx.truncated}"
    )
    lines.append("")

    if ctx.no_definition:
        lines.extend(
            [
                "## Notes",
                "",
                "No code definition resolved for this surface.",
                "",
            ]
        )
        return "\n".join(lines)

    root = ctx.root
    if root is None:
        lines.extend(["## Notes", "", "No code definition resolved for this surface.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            f"## Root: {root.module}.{root.qualname}",
            "",
            "```python",
            root.source,
            "```",
            "",
        ]
    )

    for unit in ctx.units:
        if unit.key == root.key:
            continue
        lines.extend(
            [
                f"## Callee: {unit.module}.{unit.qualname} (hop {unit.hop})",
                "",
                "```python",
                unit.source,
                "```",
                "",
            ]
        )

    if ctx.unresolved:
        lines.append("## Unresolved callees")
        lines.append("")
        for ref in ctx.unresolved:
            reason = ref.reason or "not statically resolvable"
            lines.append(f"- `{ref.expression}` — {reason}")
        lines.append("")

    if ctx.truncated:
        lines.extend(
            [
                "## Notes",
                "",
                "Collection stopped early because of --max-callees or --max-code-lines.",
                "",
            ]
        )

    return "\n".join(lines)


def run_code(
    inventory: InventoryResult,
    target: Path,
    output_dir: Path,
    *,
    depth: Depth = "body",
    scope: CalleeScope = "same-package",
    max_hops: int = 1,
    max_callees: int = 8,
    max_code_lines: int = 400,
    detect_cycles: bool = True,
    surfaces: tuple[str, ...] = (),
    verbose: bool = False,
) -> CodeStageResult:
    """Write ``code-context/<surface-id>.md`` for each selected surface."""
    target = target.resolve()
    paths = ensure_output_dir(output_dir)
    code_dir = paths.code_context_dir
    code_dir.mkdir(parents=True, exist_ok=True)

    all_edges: list[tuple[str, str]] = []
    written: list[Path] = []

    for surface in iter_surfaces_from_inventory(inventory.data, target):
        if not surface_matches(
            surface_id=surface.surface_id,
            package=surface.package,
            tokens=surfaces,
        ):
            continue

        ctx = collect_context(
            surface,
            target,
            depth=depth,
            scope=scope,
            max_hops=max_hops,
            max_callees=max_callees,
            max_code_lines=max_code_lines,
            package=surface.package,
        )
        all_edges.extend(ctx.edges)
        out_path = code_dir / f"{surface.surface_id}.md"
        body = _render_code_context_markdown(ctx, max_hops=max_hops)
        write_text(out_path, body)
        written.append(out_path)
        if verbose:
            sys.stderr.write(f"[INFO] Wrote {out_path}\n")

    cycles_path: Path | None = None
    cycle_count = 0
    if detect_cycles:
        cycles = find_cycles(all_edges)
        cycle_count = len(cycles)
        cycles_path = code_dir / "_cycles.json"
        report = CycleReport(cycles=cycles)
        write_json(
            cycles_path,
            {"cycles": report.cycles, "count": report.count},
        )
        if verbose:
            sys.stderr.write(
                f"[INFO] Wrote {cycles_path} ({cycle_count} cycle(s))\n"
            )

    return CodeStageResult(
        output_dir=paths.root,
        code_context_dir=code_dir,
        written_paths=written,
        cycles_path=cycles_path,
        cycle_count=cycle_count,
    )


def load_inventory_for_code(output_dir: Path) -> InventoryResult:
    """Load inventory or raise :class:`MissingStageInputError`."""
    data = require_inventory_json(output_dir, needed_by="code")
    paths = ensure_output_dir(output_dir)
    warnings = data.get("warnings", []) if isinstance(data.get("warnings"), list) else []
    return InventoryResult(
        inventory_path=paths.inventory_json,
        data=data,
        warnings=[str(w) for w in warnings],
    )


__all__ = ["load_inventory_for_code", "run_code"]
