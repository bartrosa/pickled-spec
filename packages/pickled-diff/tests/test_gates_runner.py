from __future__ import annotations

from pathlib import Path

from pickled_core import Verdict
from pickled_diff.gates_runner import run_all

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_run_all_passes_on_examples_workspace() -> None:
    results = run_all(_EXAMPLES)
    assert len(results) == 1
    assert results[0].gate_name == "diff.differential_oracle"
    assert results[0].verdict is Verdict.PASS


def test_run_all_warns_without_config(tmp_path: Path) -> None:
    results = run_all(tmp_path)
    assert len(results) == 1
    assert results[0].gate_name == "diff.config"
    assert results[0].verdict is Verdict.WARN
