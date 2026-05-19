"""Tests for pickled-spec check-all."""

from __future__ import annotations

from pathlib import Path

from pickled_core import Verdict
from pickled_core.check_all import run_check_all

_REPO_ROOT = Path(__file__).resolve().parents[3]
_EXAMPLE = _REPO_ROOT / "examples" / "user-management-crud"


def test_check_all_integration_example_no_fail() -> None:
    rows, exit_code = run_check_all(_EXAMPLE, warn_ok=True)
    assert exit_code == 0
    assert not any(r.verdict is Verdict.FAIL for r in rows)


def test_check_all_rules_coverage_pass() -> None:
    rows, _ = run_check_all(_EXAMPLE, warn_ok=True)
    coverage = [r for r in rows if r.package == "rules" and r.gate == "rules.coverage"]
    assert len(coverage) == 1
    assert coverage[0].verdict is Verdict.PASS


def test_check_all_warn_ok_vs_strict_exit() -> None:
    rows, code_strict = run_check_all(_EXAMPLE, warn_ok=False)
    _, code_relaxed = run_check_all(_EXAMPLE, warn_ok=True)
    assert code_relaxed == 0
    if any(r.verdict is Verdict.WARN for r in rows):
        assert code_strict == 1
