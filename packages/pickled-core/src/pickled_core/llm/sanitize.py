"""Sanitize LLM text before parsing structured outputs."""

from __future__ import annotations

import re

_FENCE_RE = re.compile(
    r"^\s*```[^\n]*\n(?P<body>.*?)\n```\s*$",
    re.DOTALL,
)


def strip_markdown_fence(text: str) -> str:
    """Strip a single outermost markdown code fence wrapping the whole text.

    If the entire stripped text is wrapped in one ```...``` fence, return the
    inner body. Otherwise return the text unchanged. Only the outermost
    full-content fence is removed; inner fences are preserved.
    """
    stripped = text.strip()
    match = _FENCE_RE.match(stripped)
    if match:
        return match.group("body").strip()
    return stripped
