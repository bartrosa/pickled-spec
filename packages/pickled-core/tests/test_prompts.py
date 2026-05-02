from __future__ import annotations

from pathlib import Path

import pytest
from pickled_core.llm.prompts import PromptTemplate, PromptTemplateError


def test_render_simple_substitution() -> None:
    tpl = PromptTemplate("Hello {{name}}")
    assert tpl.render(name="world") == "Hello world"


def test_missing_variable_raises() -> None:
    tpl = PromptTemplate("Hello {{name}}")
    with pytest.raises(PromptTemplateError, match="Missing template variables"):
        tpl.render()


def test_from_file_missing_raises() -> None:
    with pytest.raises(PromptTemplateError, match="Template not found"):
        PromptTemplate.from_file("nonexistent.md")


def test_required_vars() -> None:
    tpl = PromptTemplate("{{a}} and {{b}}")
    assert tpl.required_vars == frozenset({"a", "b"})


def test_from_file_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "draft.md"
    path.write_text("Story: {{story}}\n", encoding="utf-8")
    tpl = PromptTemplate.from_file(path)
    assert tpl.required_vars == frozenset({"story"})
    assert tpl.render(story="As a user") == "Story: As a user\n"
