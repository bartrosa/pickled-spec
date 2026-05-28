"""LLM-driven drafter: user story → Gherkin feature."""

from __future__ import annotations

from pickled_core import DraftResult, LLMClient, PromptTemplate
from pickled_core.llm.sanitize import strip_markdown_fence
from pickled_core.llm.turns import complete_prompt

from pickled_bdd.prompts import template_path


class FeatureDrafter:
    """Drafts a `.feature` file from a natural-language user story."""

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(template_path("draft.md"))

    def draft_from_story(self, story: str) -> DraftResult:
        """Send the story to the LLM and return a DraftResult.

        The drafter does not validate the returned Gherkin; that is the
        Ambiguity gate's job (PR-08). v0.1 returns the raw text and
        leaves a generic rationale string.
        """
        prompt = self._template.render(story=story)
        feature_text = complete_prompt(
            self._llm,
            prompt,
            system="You output only Gherkin. No prose, no fences.",
        )
        return DraftResult(
            text=strip_markdown_fence(feature_text),
            rationale="LLM-drafted from user story; no post-processing applied.",
            warnings=(),
        )
