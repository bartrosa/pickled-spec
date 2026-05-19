"""Read-only MCP resources over ``runs/`` and pickled configuration."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

from pickled_core.llm.config import ConfigError, load_config

if TYPE_CHECKING:
    from fastmcp import FastMCP

    from pickled_core.mcp.runtime import PickledMCPServer

_RUN_ID_RE = re.compile(r"^[0-9A-Za-z_-]{1,64}$")


def runs_dir() -> Path:
    return Path(os.environ.get("PICKLED_RUNS_DIR", "runs")).resolve()


def validate_run_id(run_id: str) -> None:
    if not _RUN_ID_RE.match(run_id):
        msg = "invalid run_id"
        raise ValueError(msg)
    if ".." in run_id or "/" in run_id or "\\" in run_id:
        raise ValueError("invalid run_id")


def resource_list_runs() -> str:
    root = runs_dir()
    rows: list[dict[str, str]] = []
    if not root.is_dir():
        return json.dumps(rows, indent=2)
    for p in sorted(root.iterdir(), key=lambda x: x.name, reverse=True):
        if p.is_dir() and _RUN_ID_RE.match(p.name):
            rows.append({"run_id": p.name})
    return json.dumps(rows, indent=2)


def resource_run_manifest(run_id: str) -> str:
    validate_run_id(run_id)
    path = runs_dir() / run_id / "manifest.json"
    if not path.is_file():
        return "{}"
    return path.read_text(encoding="utf-8")


def resource_run_llm_calls(run_id: str, limit: int) -> str:
    validate_run_id(run_id)
    path = runs_dir() / run_id / "llm_calls.jsonl"
    if not path.is_file():
        return ""
    lines = path.read_text(encoding="utf-8").splitlines()
    chunk = lines[-limit:] if limit > 0 else lines
    return "\n".join(chunk) + ("\n" if chunk else "")


def resource_config_content() -> str:
    local = Path("pickled.config.yaml")
    if local.is_file():
        return local.read_text(encoding="utf-8")
    try:
        cfg = load_config()
    except ConfigError as exc:
        return json.dumps({"ok": False, "error": str(exc)}, indent=2)
    prov: dict[str, Any] = {}
    for name, entry in cfg.providers.items():
        prov[name] = {
            "type": str(entry.type),
            "default_model": entry.default_model,
            "api_key_env": ("<redacted>" if entry.api_key_env else None),
            "base_url": entry.base_url,
        }
    return json.dumps({"ok": True, "providers": prov}, indent=2)


def register_core_resources(server: PickledMCPServer | FastMCP) -> None:
    """Attach pickled-core resources to a FastMCP or PickledMCPServer app."""
    app: FastMCP = (
        server.fastmcp_app if hasattr(server, "fastmcp_app") else server
    )

    @app.resource("pickled://runs")
    def list_runs() -> str:
        return resource_list_runs()

    @app.resource("pickled://runs/{run_id}/manifest")
    def run_manifest(run_id: str) -> str:
        return resource_run_manifest(run_id)

    @app.resource("pickled://runs/{run_id}/llm_calls/{limit}")
    def run_llm_calls(run_id: str, limit: str) -> str:
        return resource_run_llm_calls(run_id, int(limit))

    @app.resource("pickled://config")
    def config_resource() -> str:
        return resource_config_content()


__all__ = [
    "register_core_resources",
    "resource_config_content",
    "resource_list_runs",
    "resource_run_llm_calls",
    "resource_run_manifest",
    "runs_dir",
    "validate_run_id",
]
