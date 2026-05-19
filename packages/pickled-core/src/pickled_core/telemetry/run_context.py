"""Active run context for telemetry (one run_id under a runs root directory)."""

from __future__ import annotations

import hashlib
import platform
import subprocess
from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from pickled_core.cost.catalogue import load_default_catalogue
from pickled_core.llm.config import load_config
from pickled_core.telemetry.ids import generate_run_id
from pickled_core.telemetry.manifest import write_manifest

_current_run: ContextVar[RunContext | None] = ContextVar("pickled_current_run", default=None)


@dataclass(frozen=True, slots=True)
class RunContext:
    """An active gate or benchmark run."""

    run_id: str
    runs_root: Path

    @property
    def run_dir(self) -> Path:
        return self.runs_root / self.run_id


def current_run() -> RunContext | None:
    """Return the innermost active run, if any."""
    return _current_run.get()


def _git_sha_safe() -> str:
    try:
        proc = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=2,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if proc.returncode != 0:
        return ""
    sha = proc.stdout.strip()
    return sha[:40] if sha else ""


def _hostname_truncated_8() -> str:
    return platform.node()[:8]


def _config_sha256() -> str:
    local = Path("pickled.config.yaml")
    if local.is_file():
        raw = local.read_bytes()
        return hashlib.sha256(raw).hexdigest()
    _ = load_config()
    return ""


def _build_manifest(run_id: str) -> dict[str, str]:
    catalogue = load_default_catalogue()
    py = platform.python_version()
    return {
        "run_id": run_id,
        "config_sha256": _config_sha256(),
        "pricing_sha256": catalogue.content_sha256,
        "git_sha": _git_sha_safe(),
        "hostname_truncated_8": _hostname_truncated_8(),
        "python_version": py,
        "created_at_utc": datetime.now(UTC).replace(microsecond=0).isoformat(),
    }


@contextmanager
def start_run(*, runs_dir: str | Path) -> Iterator[RunContext]:
    """Create a new run directory under *runs_dir* and activate it for telemetry."""
    root = Path(runs_dir).resolve()
    run_id = generate_run_id()
    ctx = RunContext(run_id=run_id, runs_root=root)
    ctx.run_dir.mkdir(parents=True, exist_ok=True)
    manifest = _build_manifest(run_id)
    write_manifest(ctx.run_dir / "manifest.json", manifest)
    token = _current_run.set(ctx)
    try:
        yield ctx
    finally:
        _current_run.reset(token)


__all__ = ["RunContext", "current_run", "start_run"]
