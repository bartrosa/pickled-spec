"""LLM-driven drafter: natural-language intent → SQL migration."""

from __future__ import annotations

from dataclasses import dataclass

import sqlglot
from pickled_core.llm.base import LLMClient, Message
from pickled_core.llm.sanitize import strip_markdown_fence

RATIONALE_SENTINEL = "---RATIONALE---"
_DRAFT_MODEL = "claude-sonnet-4-5-20250929"


@dataclass(frozen=True, slots=True)
class DraftResult:
    text: str
    rationale: str
    warnings: tuple[str, ...]


class MigrationDrafter:
    """Draft a SQL migration from a natural-language intent."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def draft_from_intent(
        self,
        *,
        intent_text: str,
        dialect: str,
        current_schema_yaml: str | None = None,
    ) -> DraftResult:
        prompt = self._build_prompt(
            intent_text=intent_text,
            dialect=dialect,
            current_schema_yaml=current_schema_yaml,
        )
        completion = self._llm.complete(
            messages=[Message(role="user", content=prompt)],
            model=_DRAFT_MODEL,
            max_tokens=4000,
            temperature=0.0,
            stop=None,
            extras=None,
        )
        text, rationale = self._split_output(strip_markdown_fence(completion.text))
        warnings = tuple(self._validate(text, dialect=dialect))
        return DraftResult(text=text, rationale=rationale, warnings=warnings)

    def _build_prompt(
        self,
        *,
        intent_text: str,
        dialect: str,
        current_schema_yaml: str | None,
    ) -> str:
        schema_block = current_schema_yaml.strip() if current_schema_yaml else "none"
        return (
            "You are drafting a SQL migration for the pickled-data tool. Given:\n\n"
            f"- dialect: {dialect}\n"
            f"- intent: {intent_text.strip()}\n"
            f"- current schema (optional YAML): {schema_block}\n\n"
            "Emit a single SQL migration file. Use only DDL statements valid in "
            "the stated dialect. Begin with a comment line "
            "`-- intent: <one-line summary>`. "
            "Do NOT include destructive operations (DROP DATABASE, TRUNCATE entire "
            "tables without a WHERE clause is N/A for DDL). "
            f"After the SQL, emit the literal line {RATIONALE_SENTINEL!r} then "
            "1-3 sentences explaining choices."
        )

    def _split_output(self, raw: str) -> tuple[str, str]:
        if RATIONALE_SENTINEL in raw:
            text, _, rationale = raw.partition(RATIONALE_SENTINEL)
            return text.strip(), rationale.strip()
        return raw.strip(), ""

    def _validate(self, text: str, *, dialect: str) -> list[str]:
        warnings: list[str] = []
        try:
            sqlglot.parse(text, dialect=dialect)
        except Exception as exc:  # noqa: BLE001 — surface any parse failure
            warnings.append(str(exc))
        for line_no, line in enumerate(text.splitlines(), start=1):
            if "drop table" in line.lower():
                warnings.append(
                    f"destructive operation on line {line_no} "
                    f"('DROP TABLE'); confirm intent before applying"
                )
        return warnings


__all__ = ["DraftResult", "MigrationDrafter"]
