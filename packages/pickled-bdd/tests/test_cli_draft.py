"""CLI tests swap the LLM via ``PICKLED_BDD_LLM_FACTORY``.

Set ``PICKLED_BDD_LLM_FACTORY=pickled_bdd.testing:build_fake_llm`` so the
CLI loads :func:`pickled_bdd.testing.build_fake_llm` instead of calling
Anthropic. Same mechanism works for OpenAI/Ollama factories in development.
"""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner
from pickled_bdd.cli import main


def test_draft_prints_to_stdout(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_fake_llm",
    )
    story = tmp_path / "story.md"
    story.write_text("# Story\nAs a user\n", encoding="utf-8")

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ["draft", str(story)])

    assert result.exit_code == 0
    assert "Feature: CLI Smoke" in result.output


def test_draft_writes_output_file(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setenv(
        "PICKLED_BDD_LLM_FACTORY",
        "pickled_bdd.testing:build_fake_llm",
    )
    story = tmp_path / "story.md"
    story.write_text("Story", encoding="utf-8")
    out = tmp_path / "out.feature"

    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(main, ["draft", str(story), "-o", str(out)])

    assert result.exit_code == 0
    assert out.read_text(encoding="utf-8").startswith("Feature: CLI Smoke")
    assert str(out) in result.stderr
