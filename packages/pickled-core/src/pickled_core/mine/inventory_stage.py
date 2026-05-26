"""Stage 1: inventory introspection."""

from __future__ import annotations

from pathlib import Path

from pickled_core.mine import inventory_lib
from pickled_core.mine.io import ensure_output_dir, write_json
from pickled_core.mine.types import InventoryResult


def run_inventory(
    target: Path,
    output_dir: Path,
    *,
    include_mcp: bool = True,
    mcp_timeout: float = 30.0,
    verbose: bool = False,
) -> InventoryResult:
    """Introspect ``target`` and write ``inventory.json`` under ``output_dir``."""
    target = target.resolve()
    paths = ensure_output_dir(output_dir)
    inv = inventory_lib.build_inventory(
        target,
        include={"cli", "mcp", "gates", "adrs", "workspaces", "packages"},
        mcp_timeout=mcp_timeout,
        no_mcp=not include_mcp,
        verbose=verbose,
    )
    data = inv.to_dict(target)
    write_json(paths.inventory_json, data)
    if verbose:
        inventory_lib.log("INFO", f"Wrote {paths.inventory_json}")
    return InventoryResult(
        inventory_path=paths.inventory_json,
        data=data,
        warnings=list(inv.warnings),
    )


__all__ = ["run_inventory"]
