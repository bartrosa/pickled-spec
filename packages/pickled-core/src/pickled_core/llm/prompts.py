"""Tiny Markdown-based prompt template loader.

Supports a single feature: `{{variable_name}}` substitution. Anything more
elaborate (conditionals, loops) belongs in Python, not in templates.
"""

from __future__ import annotations

import re
from pathlib import Path

_VAR_PATTERN = re.compile(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}")


class PromptTemplateError(ValueError):
    """Raised when a template cannot be loaded or rendered."""


class PromptTemplate:
    """A simple `{{var}}` Markdown template.

    Usage:

        tpl = PromptTemplate.from_file("prompts/draft.md")
        prompt = tpl.render(story="As a user...")
    """

    def __init__(self, source: str) -> None:
        self._source = source
        self._required_vars = frozenset(_VAR_PATTERN.findall(source))

    @classmethod
    def from_file(cls, path: str | Path) -> PromptTemplate:
        p = Path(path)
        if not p.exists():
            raise PromptTemplateError(f"Template not found: {path}")
        return cls(p.read_text(encoding="utf-8"))

    @property
    def required_vars(self) -> frozenset[str]:
        return self._required_vars

    def render(self, **variables: str) -> str:
        missing = self._required_vars - variables.keys()
        if missing:
            raise PromptTemplateError(f"Missing template variables: {sorted(missing)}")
        return _VAR_PATTERN.sub(
            lambda m: variables[m.group(1)],
            self._source,
        )
