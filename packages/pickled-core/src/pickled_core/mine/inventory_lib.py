"""Target-repo inventory introspection (library core for mine + scripts)."""

from __future__ import annotations

import ast
import asyncio
import importlib
import json
import re
import subprocess
import sys
import tomllib
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import click

MCP_PREFIXES = ("bdd_", "rules_", "schema_", "iac_", "data_", "diff_", "core_")
GATE_METHOD_NAMES = frozenset({"run", "run_all", "evaluate", "verify"})
ADR_NUMBER_RE = re.compile(r"\b(\d{4})\b")
_GATE_RETURN_BASE = frozenset(
    {"GateResult", "CoverageReport", "MigrationDriftReport"}
)
_SKIP_WORKSPACE_PARTS = frozenset({".venv", "node_modules", ".git", "dist", "build"})


def log(level: str, msg: str) -> None:
    sys.stderr.write(f"[{level}] {msg}\n")


def _load_toml(path: Path) -> dict[str, Any]:
    return tomllib.loads(path.read_text(encoding="utf-8"))


def _project_entry_points(data: dict[str, Any]) -> dict[str, Any]:
    project = data.get("project")
    if not isinstance(project, dict):
        return {}
    eps = project.get("entry-points")
    return eps if isinstance(eps, dict) else {}


def expand_packages(target: Path) -> list[Path]:
    """Discover package roots under ``target`` (uv workspace or single project)."""
    target = target.resolve()
    root_toml = target / "pyproject.toml"
    if not root_toml.is_file():
        msg = f"pyproject.toml not found under {target}"
        raise FileNotFoundError(msg)

    data = _load_toml(root_toml)
    uv = data.get("tool", {})
    members: list[str] = []
    if isinstance(uv, dict):
        workspace = uv.get("uv", {})
        if isinstance(workspace, dict):
            ws = workspace.get("workspace", {})
            if isinstance(ws, dict):
                raw = ws.get("members", [])
                if isinstance(raw, list):
                    members = [str(m) for m in raw]

    found: list[Path] = []
    seen: set[Path] = set()
    if members:
        for pattern in members:
            for candidate in sorted(target.glob(pattern)):
                pkg_toml = candidate / "pyproject.toml"
                if pkg_toml.is_file():
                    resolved = candidate.resolve()
                    if resolved not in seen:
                        seen.add(resolved)
                        found.append(resolved)
    if not found:
        found.append(target)
    return found


def walk_click_group(group: click.Group, prefix: str = "") -> Iterator[dict[str, Any]]:
    for name, cmd in sorted(group.commands.items()):
        full = name if not prefix else f"{prefix} {name}"
        yield {
            "full_name": full,
            "help": (cmd.help or "").strip(),
            "params": [
                {
                    "name": p.name,
                    "type": type(p).__name__,
                    "required": bool(getattr(p, "required", False)),
                    "default": (
                        None
                        if p.default is None
                        else (
                            p.default.__name__
                            if callable(p.default)
                            else str(p.default)
                        )
                    ),
                    "help": (getattr(p, "help", "") or "").strip(),
                    "secondary_opts": list(getattr(p, "secondary_opts", []) or []),
                    "opts": list(getattr(p, "opts", []) or []),
                }
                for p in cmd.params
            ],
            "is_group": isinstance(cmd, click.Group),
        }
        if isinstance(cmd, click.Group):
            yield from walk_click_group(cmd, prefix=full)


def _import_click_commands(script_target: str) -> list[dict[str, Any]]:
    module_name, sep, attr = script_target.partition(":")
    if not sep:
        raise ValueError(f"invalid script target {script_target!r}")
    module = importlib.import_module(module_name)
    target = getattr(module, attr)
    if isinstance(target, click.Group):
        return list(walk_click_group(target))
    if isinstance(target, click.Command):
        return [
            {
                "full_name": target.name or attr,
                "help": (target.help or "").strip(),
                "params": [],
                "is_group": False,
            }
        ]
    raise TypeError(f"{script_target!r} is not a click command or group")


def _prepend_src_layout(pkg_dir: Path) -> None:
    """Make ``src/<package>/`` importable for hatch src-layout projects."""
    src_root = pkg_dir / "src"
    if src_root.is_dir():
        src_str = str(src_root.resolve())
        if src_str not in sys.path:
            sys.path.insert(0, src_str)


def _collect_packages(target: Path, verbose: bool) -> dict[str, dict[str, Any]]:
    packages: dict[str, dict[str, Any]] = {}
    for pkg_dir in expand_packages(target):
        _prepend_src_layout(pkg_dir)
        data = _load_toml(pkg_dir / "pyproject.toml")
        project = data.get("project", {})
        if not isinstance(project, dict):
            continue
        name = str(project.get("name", pkg_dir.name))
        scripts = project.get("scripts", {})
        if not isinstance(scripts, dict):
            scripts = {}
        entry_points = _project_entry_points(data)
        optional = project.get("optional-dependencies", {})
        opt_names = sorted(optional.keys()) if isinstance(optional, dict) else []
        packages[name] = {
            "version": str(project.get("version", "")),
            "description": str(project.get("description", "")),
            "scripts": {str(k): str(v) for k, v in scripts.items()},
            "entry_points": {
                str(k): (
                    {str(ek): str(ev) for ek, ev in v.items()}
                    if isinstance(v, dict)
                    else str(v)
                )
                for k, v in entry_points.items()
            },
            "optional_dependencies": opt_names,
            "cli_commands": [],
            "mcp_tools": [],
            "gates": [],
        }
        for script_name, script_target in scripts.items():
            try:
                commands = _import_click_commands(str(script_target))
                packages[name]["cli_commands"].extend(commands)
            except Exception as exc:
                log(
                    "WARN",
                    f"CLI introspection failed for {name} ({script_name}): "
                    f"{type(exc).__name__}: {exc}",
                )
                if verbose:
                    log("INFO", f"  target={script_target}")
    return packages


def _mcp_namespace_map(packages: dict[str, dict[str, Any]]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for pkg_name, meta in packages.items():
        eps = meta.get("entry_points", {})
        if not isinstance(eps, dict):
            continue
        sub = eps.get("pickled.mcp.subservers", {})
        if isinstance(sub, dict):
            for key in sub:
                mapping[f"{key}_"] = pkg_name
    return mapping


def _pickled_mcp_stdio_args(target: Path) -> list[str] | None:
    root_toml = target / "pyproject.toml"
    if not root_toml.is_file():
        return None
    data = _load_toml(root_toml)
    project = data.get("project", {})
    if not isinstance(project, dict):
        return None
    scripts = project.get("scripts", {})
    if not isinstance(scripts, dict) or "pickled-spec" not in scripts:
        return None
    return [
        "run",
        "--directory",
        str(target),
        "pickled-spec",
        "mcp",
        "--transport",
        "stdio",
    ]


async def _list_mcp_tools_async(target: Path, timeout: float) -> list[dict[str, Any]]:
    from mcp.client.session import ClientSession
    from mcp.client.stdio import StdioServerParameters, stdio_client

    args = _pickled_mcp_stdio_args(target)
    if args is None:
        msg = "no pickled-spec MCP entry point in target pyproject.toml"
        raise RuntimeError(msg)

    params = StdioServerParameters(command="uv", args=args, cwd=str(target))
    async with (
        stdio_client(params) as (read, write),
        ClientSession(read, write) as session,
    ):
        await session.initialize()
        result = await asyncio.wait_for(session.list_tools(), timeout=timeout)
        tools: list[dict[str, Any]] = []
        for t in result.tools:
            schema = getattr(t, "inputSchema", None)
            if schema is None and hasattr(t, "model_dump"):
                dumped = t.model_dump()
                schema = dumped.get("inputSchema") or dumped.get("input_schema")
            tools.append(
                {
                    "name": t.name,
                    "description": (t.description or "").strip(),
                    "input_schema": schema,
                }
            )
        return tools


def _bucket_mcp_tools(
    tools: list[dict[str, Any]],
    namespace_map: dict[str, str],
    packages: dict[str, dict[str, Any]],
    warnings: list[str],
) -> None:
    buckets: dict[str, list[dict[str, Any]]] = {p: [] for p in packages}
    unknown: list[dict[str, Any]] = []
    for tool in tools:
        name = str(tool["name"])
        matched_pkg: str | None = None
        for prefix, pkg in namespace_map.items():
            if name.startswith(prefix):
                matched_pkg = pkg
                break
        if matched_pkg is None:
            for prefix in MCP_PREFIXES:
                if name.startswith(prefix):
                    log("WARN", f"MCP tool {name!r} has no entry-point mapping")
                    unknown.append(tool)
                    break
            else:
                unknown.append(tool)
            continue
        buckets.setdefault(matched_pkg, []).append(tool)
    for pkg_name, items in buckets.items():
        if pkg_name in packages:
            packages[pkg_name]["mcp_tools"] = sorted(items, key=lambda x: x["name"])
    if unknown:
        if "_unknown_namespace" not in packages:
            packages["_unknown_namespace"] = {
                "version": "",
                "description": "Unmapped MCP tools",
                "scripts": {},
                "entry_points": {},
                "optional_dependencies": [],
                "cli_commands": [],
                "mcp_tools": sorted(unknown, key=lambda x: x["name"]),
                "gates": [],
            }
        warnings.append(f"{len(unknown)} MCP tool(s) in _unknown_namespace")


def _relative_path(target: Path, path: Path) -> str:
    try:
        return str(path.relative_to(target))
    except ValueError:
        return str(path)


def _gate_glob_patterns(target: Path) -> list[str]:
    if (target / "packages").is_dir():
        return [
            "packages/*/src/**/gates/**/*.py",
            "packages/*/src/**/gates.py",
            "packages/*/src/**/gates_runner.py",
        ]
    return ["**/gates/**/*.py", "**/gates.py", "**/gates_runner.py"]


def _scan_gate_files(target: Path) -> list[dict[str, Any]]:
    seen_files: set[Path] = set()
    gate_entries: list[dict[str, Any]] = []
    for pattern in _gate_glob_patterns(target):
        for path in target.glob(pattern):
            if not path.is_file() or path in seen_files:
                continue
            if _SKIP_WORKSPACE_PARTS.intersection(path.parts):
                continue
            seen_files.add(path)
            try:
                source = path.read_text(encoding="utf-8")
                tree = ast.parse(source, filename=str(path))
            except SyntaxError as exc:
                log("WARN", f"AST parse failed for {path}: {exc}")
                continue
            parts = path.relative_to(target).with_suffix("").parts
            module = ".".join(parts[3:] if len(parts) > 3 and parts[0] == "packages" else parts)
            report_types = set(_GATE_RETURN_BASE) | {
                node.name
                for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name.endswith("Report")
            }
            allowed_returns = report_types | {"GateResult"}

            for node in tree.body:
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    ann = ast.unparse(node.returns) if node.returns else None
                    if _annotation_matches(ann, allowed_returns):
                        gate_entries.append(
                            _gate_entry(
                                target, path, module, node, "function", node.name
                            )
                        )
                elif isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if not isinstance(
                            item, (ast.FunctionDef, ast.AsyncFunctionDef)
                        ):
                            continue
                        if item.name not in GATE_METHOD_NAMES:
                            continue
                        ann = ast.unparse(item.returns) if item.returns else None
                        if _annotation_matches(ann, allowed_returns):
                            gate_entries.append(
                                _gate_entry(
                                    target,
                                    path,
                                    module,
                                    item,
                                    "class",
                                    f"{node.name}.{item.name}",
                                )
                            )
    gate_entries.sort(key=lambda e: (e["module"], e["name"]))
    return gate_entries


def _gate_entry(
    target: Path,
    path: Path,
    module: str,
    node: ast.AST,
    kind: str,
    name: str,
) -> dict[str, Any]:
    doc = ast.get_docstring(node) if isinstance(
        node, (ast.AsyncFunctionDef, ast.FunctionDef, ast.ClassDef)
    ) else ""
    paragraph = (doc or "").strip().split("\n\n")[0].replace("\n", " ").strip()
    if len(paragraph) > 200:
        paragraph = paragraph[:197] + "..."
    ann = ""
    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        ann = ast.unparse(node.returns) if node.returns else ""
    return {
        "kind": kind,
        "name": name,
        "module": module,
        "file": _relative_path(target, path),
        "line": getattr(node, "lineno", 0),
        "returns": ann,
        "docstring_summary": paragraph,
    }


def _annotation_matches(ann: str | None, allowed: set[str]) -> bool:
    if not ann:
        return False
    compact = ann.replace(" ", "")
    return any(marker in compact for marker in allowed)


def _assign_gates_to_packages(
    target: Path,
    gates: list[dict[str, Any]],
    packages: dict[str, dict[str, Any]],
) -> None:
    pkg_by_module_prefix: list[tuple[str, str]] = []
    for pkg_dir in expand_packages(target):
        data = _load_toml(pkg_dir / "pyproject.toml")
        project = data.get("project", {})
        if not isinstance(project, dict):
            continue
        name = str(project.get("name", pkg_dir.name))
        module_root = name.replace("-", "_")
        pkg_by_module_prefix.append((module_root, name))
    for gate in gates:
        module = str(gate["module"])
        assigned = False
        for module_root, pkg_name in pkg_by_module_prefix:
            if module.startswith(module_root):
                packages.setdefault(pkg_name, {}).setdefault("gates", []).append(gate)
                assigned = True
                break
        if not assigned:
            log("WARN", f"Gate {gate['name']!r} not attributed to a package")


def _parse_adr_file(target: Path, path: Path) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    number = path.stem.split("-", 1)[0]
    title = ""
    status = "unknown"
    date = ""
    supersedes: list[str] = []
    superseded_by: list[str] = []

    def _section_content(heading: str) -> list[str]:
        start: int | None = None
        for i, line in enumerate(lines):
            if line.strip().lower() == f"## {heading}".lower():
                start = i + 1
                break
        if start is None:
            return []
        body: list[str] = []
        for line in lines[start:]:
            if line.startswith("## "):
                break
            body.append(line)
        return body

    for line in lines:
        if line.startswith("# ") and not title:
            title = line[2:].strip()
            break

    for line in _section_content("Status"):
        stripped = line.strip()
        if stripped and not stripped.startswith("-"):
            status = stripped.lstrip("- ").strip()
            break

    for line in _section_content("Date"):
        stripped = line.strip()
        if stripped:
            date = stripped.lstrip("- ").strip()
            break

    for heading, target_list in (("Supersedes", supersedes), ("Superseded by", superseded_by)):
        for line in _section_content(heading):
            target_list.extend(ADR_NUMBER_RE.findall(line))

    return {
        "number": number,
        "title": title,
        "status": status,
        "date": date,
        "file": _relative_path(target, path),
        "supersedes": sorted(set(supersedes)),
        "superseded_by": sorted(set(superseded_by)),
    }


def _collect_adrs(target: Path) -> list[dict[str, Any]]:
    decisions = target / "docs" / "decisions"
    if not decisions.is_dir():
        return []
    adrs: list[dict[str, Any]] = []
    for path in sorted(decisions.glob("*.md")):
        if path.name in {"0000-template.md", "README.md"}:
            continue
        if len(path.stem) < 4 or not path.stem[:4].isdigit():
            continue
        adrs.append(_parse_adr_file(target, path))
    adrs.sort(key=lambda a: a["number"])
    return adrs


def _yaml_to_json_via_uv(target: Path, yaml_text: str) -> dict[str, Any]:
    code = (
        "import json, sys, yaml; "
        "data = yaml.safe_load(sys.stdin.read()); "
        "print(json.dumps(data))"
    )
    proc = subprocess.run(
        ["uv", "run", "python", "-c", code],
        input=yaml_text,
        capture_output=True,
        text=True,
        cwd=str(target),
        check=False,
    )
    if proc.returncode != 0:
        raise RuntimeError(proc.stderr.strip() or "yaml parse failed")
    loaded = json.loads(proc.stdout)
    if loaded is None:
        return {}
    if not isinstance(loaded, dict):
        raise RuntimeError("pickled.ruleset.yaml root must be a mapping")
    return loaded


def _resolve_workspace_rulesets(
    target: Path,
    workspace_root: Path,
    cfg: dict[str, Any],
    warnings: list[str],
) -> tuple[str, list[dict[str, Any]]]:
    has_singular = "ruleset" in cfg
    has_plural = "rulesets" in cfg
    if has_singular and has_plural:
        warnings.append(
            f"{workspace_root}: pickled.ruleset.yaml has both ruleset and rulesets"
        )
        return "unknown", []

    entries: list[dict[str, Any]] = []
    if has_singular:
        rel = cfg.get("ruleset")
        if not isinstance(rel, str):
            return "unknown", entries
        resolved = (workspace_root / rel).resolve()
        short_name = str(cfg.get("ruleset_short_name", resolved.stem))
        entries.append(
            {
                "path": rel,
                "short_name": short_name,
                "exists": resolved.is_file(),
            }
        )
        return "single", entries

    if has_plural:
        raw = cfg.get("rulesets")
        if not isinstance(raw, list):
            return "unknown", entries
        for item in raw:
            if not isinstance(item, dict):
                continue
            path_raw = item.get("path")
            if not isinstance(path_raw, str):
                continue
            short_raw = item.get("short_name")
            short_name = (
                str(short_raw) if isinstance(short_raw, str) else Path(path_raw).stem
            )
            resolved = (workspace_root / path_raw).resolve()
            entries.append(
                {
                    "path": path_raw,
                    "short_name": short_name,
                    "exists": resolved.is_file(),
                }
            )
        form = "multi" if len(entries) > 1 else "single"
        return form, entries

    return "unknown", entries


def _collect_workspaces(target: Path, warnings: list[str]) -> list[dict[str, Any]]:
    configs: list[Path] = []
    for path in target.glob("**/pickled.ruleset.yaml"):
        if _SKIP_WORKSPACE_PARTS.intersection(path.parts):
            continue
        configs.append(path)
    workspaces: list[dict[str, Any]] = []
    for cfg_path in sorted(set(configs)):
        workspace_root = cfg_path.parent.resolve()
        try:
            cfg = _yaml_to_json_via_uv(target, cfg_path.read_text(encoding="utf-8"))
        except Exception as exc:
            log("WARN", f"Failed to read {cfg_path}: {exc}")
            warnings.append(f"workspace parse failed: {cfg_path}")
            continue
        form, rulesets = _resolve_workspace_rulesets(
            target, workspace_root, cfg, warnings
        )
        rel_root = _relative_path(target, workspace_root)
        features = list(workspace_root.glob("features/**/*.feature"))
        stories_dir = workspace_root / "stories"
        story_count = (
            len(list(stories_dir.glob("**/*.story.md"))) if stories_dir.is_dir() else 0
        )
        workspaces.append(
            {
                "path": rel_root,
                "config_file": _relative_path(target, cfg_path),
                "form": form,
                "rulesets": rulesets,
                "feature_count": len(features),
                "story_count": story_count,
            }
        )
    workspaces.sort(key=lambda w: w["path"])
    return workspaces


@dataclass
class Inventory:
    packages: dict[str, dict[str, Any]] = field(default_factory=dict)
    adrs: list[dict[str, Any]] = field(default_factory=list)
    workspaces: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    gate_entries: list[dict[str, Any]] = field(default_factory=list)

    def to_dict(self, target: Path) -> dict[str, Any]:
        cli_total = sum(len(p.get("cli_commands", [])) for p in self.packages.values())
        mcp_total = sum(len(p.get("mcp_tools", [])) for p in self.packages.values())
        return {
            "schema_version": "1",
            "generated_at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "repo_root": str(target.resolve()),
            "totals": {
                "packages": len(self.packages),
                "cli_commands": cli_total,
                "mcp_tools": mcp_total,
                "gates": len(self.gate_entries),
                "adrs": len(self.adrs),
                "workspaces": len(self.workspaces),
            },
            "packages": self.packages,
            "adrs": self.adrs,
            "workspaces": self.workspaces,
            "warnings": self.warnings,
        }


def build_inventory(
    target: Path,
    *,
    include: set[str] | None = None,
    mcp_timeout: float = 30.0,
    no_mcp: bool = False,
    verbose: bool = False,
) -> Inventory:
    """Introspect ``target`` and return structured inventory."""
    if include is None:
        include = {"cli", "mcp", "gates", "adrs", "workspaces", "packages"}

    inv = Inventory()
    if include & {"packages", "cli", "mcp"}:
        inv.packages = _collect_packages(target, verbose)

    if "mcp" in include and not no_mcp:
        if _pickled_mcp_stdio_args(target) is None:
            log("WARN", "MCP tools skipped (no pickled-spec script in target)")
            inv.warnings.append("MCP tools skipped: target has no pickled-spec entry point")
        else:
            try:
                tools = asyncio.run(_list_mcp_tools_async(target, mcp_timeout))
                _bucket_mcp_tools(
                    tools,
                    _mcp_namespace_map(inv.packages),
                    inv.packages,
                    inv.warnings,
                )
                if verbose:
                    log("INFO", f"MCP tools listed: {len(tools)}")
            except Exception as exc:
                log("WARN", f"MCP tools/list failed: {type(exc).__name__}: {exc}")
                inv.warnings.append("MCP tools section empty due to subprocess error")
    elif "mcp" in include and no_mcp:
        log("WARN", "MCP tools section skipped (--no-mcp)")

    if "gates" in include:
        if not inv.packages:
            inv.packages = _collect_packages(target, verbose)
        inv.gate_entries = _scan_gate_files(target)
        _assign_gates_to_packages(target, inv.gate_entries, inv.packages)

    if "adrs" in include:
        inv.adrs = _collect_adrs(target)

    if "workspaces" in include:
        inv.workspaces = _collect_workspaces(target, inv.warnings)

    return inv


def parse_include(raw: str) -> set[str]:
    parts = {p.strip().lower() for p in raw.split(",") if p.strip()}
    if "all" in parts:
        return {"cli", "mcp", "gates", "adrs", "workspaces", "packages"}
    return parts


__all__ = ["Inventory", "build_inventory", "expand_packages", "parse_include", "walk_click_group"]
