"""Workspace gate runner for ``pickled-spec check-all``."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import yaml
from pickled_core import GateResult, Verdict

from pickled_diff.comparator import ExactEqComparator, StructuralJsonComparator
from pickled_diff.corpus import CorpusItem, InMemoryCorpus
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import SubprocessRunner


def _find_config(root: Path) -> Path | None:
    for rel in ("pickled.diff.yaml", "diff/pickled.diff.yaml"):
        path = root / rel
        if path.is_file():
            return path
    return None


def _load_config(root: Path) -> dict[str, Any]:
    cfg_path = _find_config(root)
    if cfg_path is None:
        return {}
    data = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    return data if isinstance(data, dict) else {}


def _argv_list(value: object, field: str) -> list[str]:
    if not isinstance(value, list) or not value:
        raise ValueError(f"{field} must be a non-empty list of strings")
    return [str(part) for part in value]


def _resolve_argv(argv: list[str], root: Path) -> list[str]:
    """Resolve relative script paths in argv against the workspace root."""
    resolved: list[str] = []
    for i, part in enumerate(argv):
        if i == 0:
            resolved.append(part)
            continue
        candidate = root / part
        if candidate.suffix == ".py" and candidate.is_file():
            resolved.append(str(candidate.resolve()))
        else:
            resolved.append(part)
    return resolved


def _comparator(name: str) -> ExactEqComparator | StructuralJsonComparator:
    if name == "structural_json":
        return StructuralJsonComparator()
    return ExactEqComparator()


def _load_corpus(root: Path, corpus_ref: str) -> InMemoryCorpus:
    corpus_path = (root / corpus_ref).resolve()
    if not corpus_path.is_file():
        msg = f"corpus file not found: {corpus_path}"
        raise FileNotFoundError(msg)
    raw = json.loads(corpus_path.read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("corpus JSON must be a list of {name, payload} objects")
    items = [
        CorpusItem(name=str(entry["name"]), payload=str(entry["payload"]))
        for entry in raw
        if isinstance(entry, dict) and "name" in entry and "payload" in entry
    ]
    return InMemoryCorpus(items)


def run_all(workdir: Path | str) -> list[GateResult]:
    """Run differential oracle gate when ``pickled.diff.yaml`` is present."""
    root = Path(workdir).resolve()
    cfg = _load_config(root)
    if not cfg:
        return [
            GateResult(
                gate_name="diff.config",
                verdict=Verdict.WARN,
                notes="missing pickled.diff.yaml or diff/pickled.diff.yaml",
            )
        ]

    try:
        oracle_argv = _resolve_argv(_argv_list(cfg.get("oracle_command"), "oracle_command"), root)
        candidate_argv = _resolve_argv(
            _argv_list(cfg.get("candidate_command"), "candidate_command"), root
        )
        corpus_ref = cfg.get("corpus")
        if not isinstance(corpus_ref, str):
            raise ValueError('config key "corpus" must be a path string')
        comparator_name = str(cfg.get("comparator", "exact"))
        timeout = float(cfg.get("timeout_seconds", 30))
        corpus = _load_corpus(root, corpus_ref)
    except (ValueError, FileNotFoundError, json.JSONDecodeError, TypeError) as exc:
        return [
            GateResult(
                gate_name="diff.config",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        ]

    oracle_cmd = list(oracle_argv)
    candidate_cmd = list(candidate_argv)
    if oracle_cmd[0] in {"python", "python3"} and len(oracle_cmd) > 1:
        oracle_cmd[0] = sys.executable
    if candidate_cmd[0] in {"python", "python3"} and len(candidate_cmd) > 1:
        candidate_cmd[0] = sys.executable

    gate = DifferentialOracleGate(
        oracle=SubprocessRunner(
            oracle_cmd,
            name="oracle",
            timeout_seconds=timeout,
            cwd=root,
        ),
        candidate=SubprocessRunner(
            candidate_cmd,
            name="candidate",
            timeout_seconds=timeout,
            cwd=root,
        ),
        comparator=_comparator(comparator_name),
    )
    gr = gate.run(corpus)
    return [
        GateResult(
            gate_name="diff.differential_oracle",
            verdict=gr.verdict,
            findings=gr.findings,
            notes=gr.notes,
        )
    ]


__all__ = ["run_all"]
