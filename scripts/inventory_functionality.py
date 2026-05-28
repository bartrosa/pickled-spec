#!/usr/bin/env python3
"""Inventory pickled-spec CLI commands, MCP tools, gates, ADRs, and workspaces."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from pickled_core.mine import inventory_lib
from pickled_core.mine.inventory_stage import enrich_inventory_data

REPO_ROOT = Path(__file__).resolve().parent.parent


def log(level: str, msg: str) -> None:
    inventory_lib.log(level, msg)


def _render_markdown(data: dict[str, object]) -> str:
    """Render inventory markdown (legacy script output)."""
    import textwrap

    lines: list[str] = []
    max_lines = 2000

    def add(text: str = "") -> bool:
        if len(lines) >= max_lines:
            return False
        lines.append(text)
        return True

    if not add("# pickled-spec functionality inventory"):
        return "\n".join(lines)
    add()
    add(f"Generated: `{data['generated_at']}`")
    add()
    totals = data["totals"]
    if not add("## Totals"):
        return "\n".join(lines)
    add()
    add("| Metric | Count |")
    add("|--------|------:|")
    for key in ("packages", "cli_commands", "mcp_tools", "gates", "adrs", "workspaces"):
        add(f"| {key} | {totals[key]} |")
    add()
    if not add("## ADRs"):
        return "\n".join(lines)
    add()
    add("| # | Title | Status | Date |")
    add("|---|-------|--------|------|")
    for adr in data["adrs"]:
        if not add(
            f"| {adr['number']} | {adr['title']} | {adr['status']} | {adr['date']} |"
        ):
            return "\n".join(lines)
    add()
    for pkg_name in sorted(data["packages"]):
        pkg = data["packages"][pkg_name]
        if not add(f"## Package: {pkg_name}"):
            return "\n".join(lines)
        add()
        desc = pkg.get("description", "")
        if desc and not add(textwrap.fill(str(desc), width=100)):
            return "\n".join(lines)
        add()
        if not add("### CLI commands"):
            return "\n".join(lines)
        for cmd in pkg.get("cli_commands", []):
            if not add(f"- `{cmd['full_name']}` — {cmd.get('help', '')}"):
                return "\n".join(lines)
        add()
    if len(lines) >= max_lines:
        lines.append("…(truncated at 2000 lines)")
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    if not (REPO_ROOT / "pyproject.toml").is_file():
        log("ERROR", f"pyproject.toml not found under {REPO_ROOT}")
        return 2

    parser = argparse.ArgumentParser(
        description="Inventory pickled-spec CLI, MCP, gates, ADRs, and workspaces."
    )
    parser.add_argument(
        "--output",
        default="dogfood/",
        help="Output directory, or '-' for stdout JSON only.",
    )
    parser.add_argument("--format", choices=("both", "json", "md"), default="both")
    parser.add_argument(
        "--include",
        default="all",
        help="Comma-separated sections: cli,mcp,gates,adrs,workspaces,all.",
    )
    parser.add_argument("--mcp-timeout", type=float, default=30.0)
    parser.add_argument("--no-mcp", action="store_true")
    parser.add_argument("--verbose", action="store_true")
    args = parser.parse_args(argv)

    include = inventory_lib.parse_include(args.include)
    inv = inventory_lib.build_inventory(
        REPO_ROOT,
        include=include,
        mcp_timeout=args.mcp_timeout,
        no_mcp=args.no_mcp,
        verbose=args.verbose,
    )
    payload = inv.to_dict(REPO_ROOT)
    enrich_inventory_data(payload, REPO_ROOT)

    emit_json = args.format in ("both", "json")
    emit_md = args.format in ("both", "md")

    if args.output == "-":
        if not emit_json:
            log("ERROR", "--output - requires --format json")
            return 2
        sys.stdout.write(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
        return 0

    out_dir = Path(args.output)
    if not out_dir.is_absolute():
        out_dir = REPO_ROOT / out_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    if emit_json:
        json_path = out_dir / "inventory.json"
        json_path.write_text(
            json.dumps(payload, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        if args.verbose:
            log("INFO", f"Wrote {json_path}")

    if emit_md:
        md_path = out_dir / "inventory.md"
        md_path.write_text(_render_markdown(payload), encoding="utf-8")
        if args.verbose:
            log("INFO", f"Wrote {md_path}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
