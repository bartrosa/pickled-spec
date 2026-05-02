"""CLI `check` tests use ``PICKLED_BDD_LLM_FACTORY`` like PR-07."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner
from pickled_bdd.cli import main

FEATURE = Path(__file__).resolve().parent.parent / "examples" / "password_reset.feature"


def test_check_exit_zero_and_pass(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_check_pass_llm",
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["check", str(FEATURE)],
        catch_exceptions=False,
    )
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["verdict"] == "pass"


def test_check_exit_one_and_warn(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_check_warn_llm",
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        ["check", str(FEATURE)],
        catch_exceptions=False,
    )
    assert result.exit_code == 1
    data = json.loads(result.output)
    assert data["verdict"] == "warn"
    assert len(data["findings"]) >= 1
