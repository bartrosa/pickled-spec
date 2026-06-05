"""Regression: ``pickled-schema`` CLI must honor ``budget.max_cost_usd`` cap.

Mirror of ``pickled-iac``'s budget-bootstrap regression. See that test
module's docstring for the full bug context: the older CLI shortcut
bypassed :func:`pickled_core.llm.bootstrap.build_default_client` and
therefore never installed the user-configured :class:`BudgetGuard`.
``pickled-schema draft`` (which retries the LLM up to 3 times) would
silently ignore ``budget.max_cost_usd`` until this fix.
"""

from __future__ import annotations

from collections.abc import Generator
from decimal import Decimal
from pathlib import Path

import pytest


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "PICKLED_SCHEMA_LLM_FACTORY",
        "PICKLED_CACHE_DIR",
        "PICKLED_CACHE_MODE",
        "PICKLED_MAX_COST_USD",
        "PICKLED_LLM_PROVIDER",
    ):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_budget_guard() -> Generator[None, None, None]:
    from pickled_core.llm.budget_context import set_budget_guard

    set_budget_guard(None)
    yield
    set_budget_guard(None)


def _write_config(tmp_path: Path, cap: str) -> Path:
    cfg = tmp_path / "pickled.config.yaml"
    cfg.write_text(
        f"""providers:
  anthropic:
    type: anthropic
    default_model: claude-test
    api_key_env: TEST_API_KEY
budget:
  max_cost_usd: \"{cap}\"
cache:
  mode: off
""",
        encoding="utf-8",
    )
    return cfg


def test_schema_cli_install_budget_guard_from_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    _write_config(tmp_path, "0.50")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TEST_API_KEY", "fake")

    from pickled_core.llm.budget_context import active_budget_guard
    from pickled_schema.cli import _build_llm_client

    assert active_budget_guard() is None
    _build_llm_client()
    guard = active_budget_guard()
    assert guard is not None, (
        "pickled-schema CLI bypassed the budget guard; users' max_cost_usd "
        "cap would not have been enforced (see this module's docstring)."
    )
    assert guard._budget.max_cost_usd == Decimal("0.50")


def test_schema_cli_install_budget_guard_from_env(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    _write_config(tmp_path, "0.50")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TEST_API_KEY", "fake")
    monkeypatch.setenv("PICKLED_MAX_COST_USD", "2.00")

    from pickled_core.llm.budget_context import active_budget_guard
    from pickled_schema.cli import _build_llm_client

    _build_llm_client()
    guard = active_budget_guard()
    assert guard is not None
    assert guard._budget.max_cost_usd == Decimal("2.00")


def test_schema_cli_factory_env_shortcut_still_works(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv(
        "PICKLED_SCHEMA_LLM_FACTORY",
        "pickled_bdd.testing:build_fake_llm",
    )
    from pickled_bdd.testing import CannedLLMClient
    from pickled_schema.cli import _build_llm_client

    client = _build_llm_client()
    assert isinstance(client, CannedLLMClient)
