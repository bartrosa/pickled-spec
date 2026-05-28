"""Stage 1: inventory introspection."""

from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

from pickled_core.mine import inventory_lib
from pickled_core.mine.inventory_lib import discover_umbrella_mcp_launch
from pickled_core.mine.io import ensure_output_dir, write_json
from pickled_core.mine.types import InventoryResult

_ADR_TITLE_PREFIX_RE = re.compile(
    r"^ADR[-\s]?(\d{4})\s*:\s*",
    re.IGNORECASE,
)
_STATUS_FRONTMATTER_RE = re.compile(
    r"^\s*[-*]?\s*(?:\*\*)?Status(?:\*\*)?\s*:\s*(.+?)\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_STATUS_MARKDOWN_RE = re.compile(r"[*_`]+")
_GLOBAL_ADR_TITLE_MARKERS = ("workspace", "monorepo", "pickled-core")
_DOCSTRING_CAP = 500


def _normalize_adr_status(raw: str) -> str:
    text = raw.strip().lstrip("- ").strip()
    if ":" in text:
        text = text.split(":", 1)[1].strip()
    text = _STATUS_MARKDOWN_RE.sub("", text).strip()
    return text or "unknown"


def _relative_path(target: Path, path: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def _first_paragraph_docstring(
    node: ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef,
) -> str:
    doc = ast.get_docstring(node)
    if not doc:
        return ""
    paragraph = doc.strip().split("\n\n")[0].replace("\n", " ").strip()
    if len(paragraph) > _DOCSTRING_CAP:
        return paragraph[: _DOCSTRING_CAP - 3] + "..."
    return paragraph


def parse_adr_file(target: Path, path: Path) -> dict[str, Any]:
    """Parse one ADR markdown file with clean title and status."""
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    number_match = re.match(r"^(\d{4})", path.stem)
    number = number_match.group(1) if number_match else path.stem[:4]

    title = ""
    for line in lines:
        if line.startswith("# "):
            raw = line[2:].strip()
            title = _ADR_TITLE_PREFIX_RE.sub("", raw).strip()
            break

    status = "unknown"
    in_status_section = False
    for line in lines:
        stripped = line.strip()
        if stripped.lower() == "## status":
            in_status_section = True
            continue
        if in_status_section:
            if stripped.startswith("## "):
                break
            if stripped:
                status = _normalize_adr_status(stripped)
                break

    if status == "unknown":
        fm = _STATUS_FRONTMATTER_RE.search(text)
        if fm:
            status = _normalize_adr_status(fm.group(1))

    date = ""
    in_date = False
    for line in lines:
        if line.strip().lower() == "## date":
            in_date = True
            continue
        if in_date:
            if line.startswith("## "):
                break
            if line.strip():
                date = line.strip()
                break

    return {
        "number": number,
        "title": title,
        "status": status,
        "date": date,
        "file": _relative_path(target, path),
        "body": text,
        "supersedes": [],
        "superseded_by": [],
    }


def collect_adrs(target: Path) -> list[dict[str, Any]]:
    """Collect ADRs from ``docs/decisions`` using enhanced parsing."""
    decisions = target / "docs" / "decisions"
    if not decisions.is_dir():
        return []
    adrs: list[dict[str, Any]] = []
    for path in sorted(decisions.glob("*.md")):
        if path.name in {"0000-template.md", "README.md"}:
            continue
        if len(path.stem) < 4 or not path.stem[:4].isdigit():
            continue
        adrs.append(parse_adr_file(target, path))
    adrs.sort(key=lambda a: a["number"])
    return adrs


def collect_adrs_from_dir(target: Path, decisions_dir: Path) -> list[dict[str, Any]]:
    """Collect ADRs from an arbitrary decisions directory (tests)."""
    adrs: list[dict[str, Any]] = []
    for path in sorted(decisions_dir.glob("*.md")):
        if path.name in {"0000-template.md", "README.md"}:
            continue
        if len(path.stem) < 4 or not path.stem[:4].isdigit():
            continue
        adrs.append(parse_adr_file(target, path))
    adrs.sort(key=lambda a: a["number"])
    return adrs


def _enrich_gate_docstring(target: Path, gate: dict[str, Any]) -> None:
    rel = gate.get("file")
    if not isinstance(rel, str) or not rel:
        return
    path = target / rel
    if not path.is_file():
        return
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except SyntaxError:
        return

    name = str(gate.get("name", ""))
    if gate.get("kind") == "class" and "." in name:
        class_name, method_name = name.split(".", 1)
        class_node: ast.ClassDef | None = None
        method_node: ast.FunctionDef | ast.AsyncFunctionDef | None = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                class_node = node
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
                        item.name == method_name
                    ):
                        method_node = item
                        break
                break
        summary = ""
        if class_node is not None:
            summary = _first_paragraph_docstring(class_node)
        if not summary and method_node is not None:
            summary = _first_paragraph_docstring(method_node)
        if summary:
            gate["docstring_summary"] = summary
        return

    for walk_node in ast.walk(tree):
        if isinstance(walk_node, (ast.FunctionDef, ast.AsyncFunctionDef)) and (
            walk_node.name == name
        ):
            summary = _first_paragraph_docstring(walk_node)
            if summary:
                gate["docstring_summary"] = summary
            return


def _enrich_gates_in_packages(data: dict[str, Any], target: Path) -> None:
    packages = data.get("packages", {})
    if not isinstance(packages, dict):
        return
    for pkg in packages.values():
        if not isinstance(pkg, dict):
            continue
        for gate in pkg.get("gates", []):
            if isinstance(gate, dict):
                _enrich_gate_docstring(target, gate)


def _camel_case_tokens(name: str) -> set[str]:
    parts = re.findall(r"[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\b)", name)
    return {p.lower() for p in parts if len(p) >= 5}


def _surface_tokens(package: str, surface_id: str, surface_name: str) -> set[str]:
    """Distinctive tokens for ADR matching (not bare monorepo package prefixes)."""
    tokens: set[str] = set()
    pkg = package.lower().strip()
    if pkg:
        tokens.add(pkg)
        tokens.add(pkg.replace("-", "_"))
    shared_prefix = pkg.split("-", 1)[0] if "-" in pkg else ""
    for raw in (surface_id, surface_name):
        for part in re.split(r"[^a-zA-Z0-9]+", raw.lower()):
            if len(part) < 5:
                continue
            if part in tokens:
                continue
            if shared_prefix and part == shared_prefix:
                continue
            tokens.add(part)
    tokens.update(_camel_case_tokens(surface_name))
    return tokens


def _adr_matches_surface(
    adr: dict[str, Any],
    *,
    package: str,
    surface_id: str,
    surface_name: str,
) -> bool:
    title = str(adr.get("title", "")).lower()
    body = str(adr.get("body", "")).lower()
    pkg = package.lower().strip()
    if pkg and (pkg in title or pkg.replace("-", "_") in title):
        return True
    leaf = pkg.split("-", 1)[-1] if "-" in pkg else ""
    if len(leaf) >= 4 and re.search(rf"\b{re.escape(leaf)}\b", title):
        return True
    tokens = _surface_tokens(package, surface_id, surface_name)
    for token in tokens:
        if token in (pkg, pkg.replace("-", "_")):
            continue
        if re.search(rf"\b{re.escape(token)}\b", title):
            return True
        if len(token) >= 8 and re.search(rf"\b{re.escape(token)}\b", body):
            return True
    return False


def _is_global_adr(adr: dict[str, Any]) -> bool:
    title = str(adr.get("title", "")).lower()
    return any(marker in title for marker in _GLOBAL_ADR_TITLE_MARKERS)


def relevant_adrs_for_surface(
    adrs: list[dict[str, Any]],
    *,
    package: str,
    surface_id: str,
    surface_name: str,
) -> list[dict[str, Any]]:
    """Return ADRs relevant to one surface (specific matches first)."""
    specific: list[dict[str, Any]] = []
    for adr in adrs:
        if _adr_matches_surface(
            adr, package=package, surface_id=surface_id, surface_name=surface_name
        ):
            specific.append({**adr, "general": False})
    if specific:
        return specific

    if package not in ("pickled-core", "pickled-spec"):
        return []

    global_hits = [
        {**adr, "general": True}
        for adr in adrs
        if _is_global_adr(adr)
    ]
    return global_hits[:1]


def enrich_inventory_data(data: dict[str, Any], target: Path) -> None:
    """Apply docstring, ADR, and per-surface ADR relevance fixes."""
    data["adrs"] = collect_adrs(target)
    _enrich_gates_in_packages(data, target)
    from pickled_core.mine.stories_stage import compute_surface_relevant_adrs

    data["surface_relevant_adrs"] = compute_surface_relevant_adrs(data)


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
    enrich_inventory_data(data, target)
    write_json(paths.inventory_json, data)
    if verbose:
        inventory_lib.log("INFO", f"Wrote {paths.inventory_json}")
    return InventoryResult(
        inventory_path=paths.inventory_json,
        data=data,
        warnings=list(inv.warnings),
    )


__all__ = [
    "collect_adrs",
    "collect_adrs_from_dir",
    "discover_umbrella_mcp_launch",
    "enrich_inventory_data",
    "parse_adr_file",
    "relevant_adrs_for_surface",
    "run_inventory",
]
