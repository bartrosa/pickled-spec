"""LLM-driven drafter: seed examples → expanded differential corpus."""

from __future__ import annotations

import json
from dataclasses import dataclass

from pickled_core.llm.base import LLMClient, Message

RATIONALE_SENTINEL = "---RATIONALE---"
_DRAFT_MODEL = "claude-sonnet-4-5-20250929"


@dataclass(frozen=True, slots=True)
class CorpusDraftResult:
    items: tuple[dict[str, str], ...]
    rationale: str
    warnings: tuple[str, ...]


class CorpusDrafter:
    """Expand seed examples into a larger test corpus."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def draft_from_examples(
        self,
        *,
        seed_examples: list[dict[str, str]],
        target_size: int,
        notes: str | None = None,
    ) -> CorpusDraftResult:
        prompt = self._build_prompt(
            seed_examples=seed_examples,
            target_size=target_size,
            notes=notes,
        )
        completion = self._llm.complete(
            messages=[Message(role="user", content=prompt)],
            model=_DRAFT_MODEL,
            max_tokens=4000,
            temperature=0.0,
            stop=None,
            extras=None,
        )
        text, rationale = self._split_output(completion.text)
        items, warnings = self._validate(text, target_size=target_size)
        return CorpusDraftResult(
            items=items,
            rationale=rationale,
            warnings=warnings,
        )

    def _build_prompt(
        self,
        *,
        seed_examples: list[dict[str, str]],
        target_size: int,
        notes: str | None,
    ) -> str:
        seeds_json = json.dumps(seed_examples, indent=2)
        notes_line = notes.strip() if notes else ""
        return (
            "You are expanding a corpus of test inputs for differential testing.\n"
            f"Given {len(seed_examples)} seed examples, produce a corpus of exactly "
            f"{target_size} total items (you may include the seeds verbatim and add "
            "new ones). Each item is "
            '`{"name": "<unique slug>", "payload": "<input value>"}`.\n'
            "Aim for diversity: edge cases (empty, large, unicode, boundary "
            "numerics), realistic mid-size inputs, and degenerate cases. Output "
            "ONLY a JSON array of objects — no preamble, no markdown fences.\n"
            f"Seed examples:\n{seeds_json}\n"
            + (f"Notes:\n{notes_line}\n" if notes_line else "")
            + f"After the JSON, emit {RATIONALE_SENTINEL!r} then 1-3 sentences."
        )

    def _split_output(self, raw: str) -> tuple[str, str]:
        if RATIONALE_SENTINEL in raw:
            text, _, rationale = raw.partition(RATIONALE_SENTINEL)
            return text.strip(), rationale.strip()
        return raw.strip(), ""

    def _validate(
        self, text: str, *, target_size: int
    ) -> tuple[tuple[dict[str, str], ...], tuple[str, ...]]:
        warnings: list[str] = []
        try:
            parsed = json.loads(text)
        except json.JSONDecodeError as exc:
            warnings.append(str(exc))
            return (), tuple(warnings)

        if not isinstance(parsed, list):
            warnings.append("corpus JSON must be an array")
            return (), tuple(warnings)

        items: list[dict[str, str]] = []
        for index, element in enumerate(parsed):
            if not isinstance(element, dict):
                warnings.append(f"item {index} must be an object")
                continue
            name = element.get("name")
            payload = element.get("payload")
            if not isinstance(name, str) or not isinstance(payload, str):
                warnings.append(f"item {index} must have string name and payload")
                continue
            items.append({"name": name, "payload": payload})

        if len(items) != target_size:
            warnings.append(
                f"corpus has {len(items)} items; expected {target_size}"
            )

        return tuple(items), tuple(warnings)


__all__ = ["CorpusDraftResult", "CorpusDrafter"]
