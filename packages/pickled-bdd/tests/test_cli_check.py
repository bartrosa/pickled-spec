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


def test_ambiguity_alias_equivalent_to_check_gate_ambiguity(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_check_pass_llm",
    )
    runner = CliRunner()
    via_check = runner.invoke(
        main,
        ["check", str(FEATURE), "--gate", "ambiguity"],
        catch_exceptions=False,
    )
    via_alias = runner.invoke(
        main,
        ["ambiguity", str(FEATURE)],
        catch_exceptions=False,
    )
    assert via_check.exit_code == via_alias.exit_code == 0
    check_data = json.loads(via_check.output)
    alias_json = via_alias.output[via_alias.output.index("{") :]
    alias_data = json.loads(alias_json)
    assert check_data["verdict"] == alias_data["verdict"] == "pass"
    assert check_data["gate"] == alias_data["gate"] == "ambiguity"
