"""Tests for :func:`pickled_core.llm.bootstrap.build_default_client`."""

from __future__ import annotations

from collections.abc import Generator
from decimal import Decimal
from pathlib import Path

import pytest
from pickled_bdd.testing import CannedLLMClient
from pickled_core.llm.bootstrap import build_default_client
from pickled_core.llm.budget_context import active_budget_guard, set_budget_guard
from pickled_core.llm.config import ConfigError, load_config


def _write_config(tmp_path: Path, body: str) -> Path:
    path = tmp_path / "pickled.config.yaml"
    path.write_text(body, encoding="utf-8")
    return path


def _anthropic_yaml(name: str = "anthropic", model: str = "claude-test") -> str:
    return f"""providers:
  {name}:
    type: anthropic
    default_model: {model}
    api_key_env: TEST_API_KEY
"""


@pytest.fixture(autouse=True)
def _clear_env(monkeypatch: pytest.MonkeyPatch) -> None:
    for key in (
        "PICKLED_BDD_LLM_FACTORY",
        "PICKLED_SCHEMA_LLM_FACTORY",
        "PICKLED_IAC_LLM_FACTORY",
        "PICKLED_CACHE_DIR",
        "PICKLED_CACHE_MODE",
        "PICKLED_MAX_COST_USD",
        "PICKLED_LLM_PROVIDER",
    ):
        monkeypatch.delenv(key, raising=False)


@pytest.fixture(autouse=True)
def _reset_budget_guard() -> Generator[None, None, None]:
    set_budget_guard(None)
    yield
    set_budget_guard(None)


def test_factory_env_shortcut_takes_precedence(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    _write_config(
        tmp_path,
        _anthropic_yaml()
        + "\ncache:\n  mode: off\n",
    )
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_fake_llm",
    )
    client = build_default_client(
        factory_env="PICKLED_BDD_LLM_FACTORY",
        config=load_config(tmp_path / "pickled.config.yaml"),
    )
    assert isinstance(client, CannedLLMClient)


def test_factory_env_invalid_format_raises_configerror(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("PICKLED_TEST_FACTORY", "no-colon-here")
    with pytest.raises(ConfigError, match="module:callable"):
        build_default_client(factory_env="PICKLED_TEST_FACTORY")


def test_no_cache_section_yields_default_read_write_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    path = _write_config(tmp_path, _anthropic_yaml())
    monkeypatch.setenv("TEST_API_KEY", "fake")
    client = build_default_client(config=load_config(path))
    assert isinstance(client, AnthropicClient)
    assert client._cache is not None


def test_cache_mode_off_yields_no_cache(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    path = _write_config(
        tmp_path,
        _anthropic_yaml() + "\ncache:\n  mode: off\n",
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    client = build_default_client(config=load_config(path))
    assert isinstance(client, AnthropicClient)
    assert client._cache is None


def test_env_cache_dir_overrides_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    path = _write_config(
        tmp_path,
        _anthropic_yaml()
        + "\ncache:\n  dir: /tmp/a\n  mode: read_write\n",
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    monkeypatch.setenv("PICKLED_CACHE_DIR", str(tmp_path / "cache-b"))
    client = build_default_client(config=load_config(path))
    assert isinstance(client, AnthropicClient)
    assert client._cache is not None
    assert client._cache._root == (tmp_path / "cache-b").resolve()


def test_env_cache_mode_invalid_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")

    path = _write_config(tmp_path, _anthropic_yaml())
    monkeypatch.setenv("TEST_API_KEY", "fake")
    monkeypatch.setenv("PICKLED_CACHE_MODE", "bogus")
    with pytest.raises(ConfigError, match="PICKLED_CACHE_MODE"):
        build_default_client(config=load_config(path))


def test_relative_cache_dir_resolves_against_config_parent(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_path = cfg_dir / "pickled.config.yaml"
    config_path.write_text(
        _anthropic_yaml() + "\ncache:\n  dir: cache\n  mode: read_write\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    cfg = load_config(config_path)
    assert cfg.source_path == config_path.resolve()
    client = build_default_client(config=cfg)
    assert isinstance(client, AnthropicClient)
    assert client._cache is not None
    assert client._cache._root == (cfg_dir / "cache").resolve()


def test_env_cache_dir_is_cwd_relative_when_relative(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    cfg_dir = tmp_path / "cfg"
    cfg_dir.mkdir()
    config_path = cfg_dir / "pickled.config.yaml"
    config_path.write_text(_anthropic_yaml(), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("TEST_API_KEY", "fake")
    monkeypatch.setenv("PICKLED_CACHE_DIR", "cache")
    client = build_default_client(config=load_config(config_path))
    assert isinstance(client, AnthropicClient)
    assert client._cache is not None
    assert client._cache._root == (tmp_path / "cache").resolve()


def test_budget_max_cost_usd_installs_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")

    path = _write_config(
        tmp_path,
        _anthropic_yaml() + '\nbudget:\n  max_cost_usd: "1.50"\n',
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    build_default_client(config=load_config(path))
    guard = active_budget_guard()
    assert guard is not None
    assert guard._budget.max_cost_usd == Decimal("1.50")


def test_budget_env_overrides_yaml(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")

    path = _write_config(
        tmp_path,
        _anthropic_yaml() + '\nbudget:\n  max_cost_usd: "1.50"\n',
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    monkeypatch.setenv("PICKLED_MAX_COST_USD", "2.00")
    build_default_client(config=load_config(path))
    guard = active_budget_guard()
    assert guard is not None
    assert guard._budget.max_cost_usd == Decimal("2.00")


def test_budget_no_cap_installs_no_guard(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")

    path = _write_config(tmp_path, _anthropic_yaml())
    monkeypatch.setenv("TEST_API_KEY", "fake")
    before = active_budget_guard()
    build_default_client(config=load_config(path))
    assert active_budget_guard() is before


def test_budget_invalid_decimal_raises(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")

    path = _write_config(
        tmp_path,
        _anthropic_yaml() + '\nbudget:\n  max_cost_usd: "not-a-number"\n',
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    with pytest.raises(ConfigError, match="decimal string"):
        build_default_client(config=load_config(path))


def test_provider_env_override(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("openai")
    from pickled_core.llm.providers.openai_compat import OpenAICompatClient

    body = """providers:
  default:
    type: openai_compat
    base_url: http://default.local/v1
    default_model: m1
  alt:
    type: openai_compat
    base_url: http://alt.local/v1
    default_model: m2
"""
    path = _write_config(tmp_path, body)
    monkeypatch.setenv("PICKLED_LLM_PROVIDER", "alt")
    client = build_default_client(config=load_config(path))
    assert isinstance(client, OpenAICompatClient)
    assert str(client._client.base_url).rstrip("/") == "http://alt.local/v1"


def test_client_default_model_threaded_from_config(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    pytest.importorskip("anthropic")
    from pickled_core.llm.providers.anthropic import AnthropicClient

    path = _write_config(
        tmp_path,
        """providers:
  anthropic:
    type: anthropic
    default_model: claude-sonnet-4-5-20250929
    api_key_env: TEST_API_KEY
""",
    )
    monkeypatch.setenv("TEST_API_KEY", "fake")
    client = build_default_client(config=load_config(path))
    assert isinstance(client, AnthropicClient)
    assert client.default_model == "claude-sonnet-4-5-20250929"
