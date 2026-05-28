"""LLM-driven drafter: natural-language brief → YAML rule set."""

from __future__ import annotations

from dataclasses import dataclass

from pickled_core.llm.base import LLMClient, Message
from pickled_core.llm.sanitize import strip_markdown_fence

from pickled_rules.loader import RuleSetValidationError, load_ruleset_from_text

RATIONALE_SENTINEL = "---RATIONALE---"
_DRAFT_MODEL = "claude-sonnet-4-5-20250929"

# Tokens that must not appear in drafted YAML (see prompt + validation).
_FORBIDDEN_TOKENS: frozenset[str] = frozenset(
    {
        "gdpr",
        "hipaa",
        "pci",
        "sox",
        "iso27001",
        "compliance",
        "regulator",
        "regulatory",
        "legal",
        "law",
        "lawful",
    }
)


@dataclass(frozen=True, slots=True)
class DraftResult:
    text: str
    rationale: str
    warnings: tuple[str, ...]


class RuleSetDrafter:
    """Draft a YAML rule set from a natural-language brief."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def draft_from_brief(
        self,
        *,
        brief_text: str,
        ruleset_short_name: str,
        source_id: str,
        applies_to: str,
        active_from: str,
    ) -> DraftResult:
        prompt = self._build_prompt(
            brief_text=brief_text,
            ruleset_short_name=ruleset_short_name,
            source_id=source_id,
            applies_to=applies_to,
            active_from=active_from,
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
        warnings = tuple(self._validate(text))
        return DraftResult(text=text, rationale=rationale, warnings=warnings)

    def _build_prompt(
        self,
        *,
        brief_text: str,
        ruleset_short_name: str,
        source_id: str,
        applies_to: str,
        active_from: str,
    ) -> str:
        banned = ", ".join(sorted(_FORBIDDEN_TOKENS))
        return (
            "You are drafting a YAML rule set for the pickled-rules tool. "
            "The input is a natural-language brief describing a domain. "
            "Emit YAML matching this schema exactly:\n\n"
            "```yaml\n"
            "metadata:\n"
            f'  source_id: "{source_id}"\n'
            '  source_title: "<concise>"\n'
            f'  applies_to: "{applies_to}"\n'
            '  maintainer: "drafted by LLM"\n'
            '  source_version: "0.1"\n'
            f'  active_from: "{active_from}"\n'
            "rules:\n"
            '  - id: "<unique kebab-case>"\n'
            '    title: "<5-10 words>"\n'
            '    description: "<one paragraph>"\n'
            '    enforcement: "strict" | "advisory" | "informational"\n'
            "```\n\n"
            f"Ruleset short name (for tagging): {ruleset_short_name}\n\n"
            "Brief:\n"
            f"{brief_text.strip()}\n\n"
            "Rules MUST use neutral, vendor-agnostic phrasing. "
            f"Do NOT include any of these tokens (case-insensitive): {banned}. "
            "Domain-specific terms belong only inside description: fields.\n\n"
            f"After the YAML, emit the literal line {RATIONALE_SENTINEL!r} then "
            "1-3 sentences explaining your rule selection."
        )

    def _split_output(self, raw: str) -> tuple[str, str]:
        if RATIONALE_SENTINEL in raw:
            text, _, rationale = raw.partition(RATIONALE_SENTINEL)
            return text.strip(), rationale.strip()
        return raw.strip(), ""

    def _validate(self, text: str) -> list[str]:
        warnings: list[str] = []
        try:
            load_ruleset_from_text(text)
        except RuleSetValidationError as exc:
            warnings.append(str(exc))
        lowered = text.lower()
        for token in sorted(_FORBIDDEN_TOKENS):
            if token in lowered:
                warnings.append(
                    f"forbidden token '{token}' in YAML; rewrite the rule"
                )
        return warnings


__all__ = ["DraftResult", "RuleSetDrafter"]
