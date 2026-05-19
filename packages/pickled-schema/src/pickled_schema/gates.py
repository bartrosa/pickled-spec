"""Format-agnostic compensating gates for pickled-schema."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pickled_core import GateResult, LLMClient, PromptTemplate, Verdict

from pickled_schema.prompts import template_path
from pickled_schema.types import SchemaArtifact

_ENDPOINT_TAG_RE = re.compile(
    r"@schema:endpoint:(GET|POST|PUT|PATCH|DELETE)-(/[^\s@]+)"
)


@dataclass(frozen=True, slots=True)
class SchemaCoverageFinding:
    """A feature tag with no matching path in the OpenAPI spec."""

    tag: str
    source: str


class SchemaAmbiguityGate:
    """Second LLM critic pass on a drafted SchemaArtifact."""

    name = "schema_ambiguity"

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm
        self._template = PromptTemplate.from_file(template_path("ambiguity.md"))

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, SchemaArtifact):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected SchemaArtifact, got {type(target).__name__}",
            )
        gherkin = ctx.get("gherkin_context")
        if not isinstance(gherkin, str) or not gherkin.strip():
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context must contain non-empty "gherkin_context"',
            )

        prompt = self._template.render(
            gherkin_context=gherkin,
            schema_yaml=target.content,
        )
        from pickled_core.llm.turns import complete_prompt

        response = complete_prompt(
            self._llm,
            prompt,
            system=(
                "Reply with a single JSON object only. "
                "No markdown fences, no commentary outside JSON."
            ),
        )
        parsed = _parse_ambiguity_response(response)
        if parsed is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes="LLM returned malformed JSON",
            )

        ambiguities = parsed.get("ambiguities", [])
        if not isinstance(ambiguities, list):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='LLM JSON missing list field "ambiguities"',
            )

        if not ambiguities:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="No ambiguities reported.",
            )

        notes = f"{len(ambiguities)} ambiguity(ies) reported."
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.WARN,
            findings=tuple(ambiguities),
            notes=notes,
        )


class SchemaCoverageGate:
    """Verify @schema:endpoint:* tags in features exist in an OpenAPI spec."""

    name = "schema_coverage"

    def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        ctx = context or {}
        if not isinstance(target, dict):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected parsed OpenAPI dict, got {type(target).__name__}",
            )

        feature_paths: list[Path] = []
        raw_paths = ctx.get("feature_paths")
        if isinstance(raw_paths, list):
            feature_paths = [Path(p) for p in raw_paths]

        feature_texts: list[tuple[str, str]] = []
        raw_texts = ctx.get("feature_texts")
        if isinstance(raw_texts, list):
            for i, text in enumerate(raw_texts):
                if isinstance(text, str):
                    feature_texts.append((f"<feature-{i}>", text))

        if not feature_paths and not feature_texts:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes='context needs "feature_paths" and/or "feature_texts"',
            )

        missing: list[SchemaCoverageFinding] = []
        for path in feature_paths:
            text = path.read_text(encoding="utf-8")
            missing.extend(
                _missing_tags(target, text, source=str(path)),
            )
        for source, text in feature_texts:
            missing.extend(_missing_tags(target, text, source=source))

        if not missing:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="All @schema:endpoint tags have matching paths.",
            )

        lines = [f"{f.tag} ({f.source})" for f in missing]
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.FAIL,
            findings=tuple(missing),
            notes="Missing endpoints: " + "; ".join(lines),
        )


def _missing_tags(
    spec: dict[str, Any],
    feature_text: str,
    *,
    source: str,
) -> list[SchemaCoverageFinding]:
    out: list[SchemaCoverageFinding] = []
    for match in _ENDPOINT_TAG_RE.finditer(feature_text):
        method, path = match.group(1), match.group(2)
        tag = match.group(0)
        if not _spec_has_endpoint(spec, method, path):
            out.append(SchemaCoverageFinding(tag=tag, source=source))
    return out


def _spec_has_endpoint(spec: dict[str, Any], method: str, path: str) -> bool:
    paths = spec.get("paths")
    if not isinstance(paths, dict) or path not in paths:
        return False
    item = paths[path]
    if not isinstance(item, dict):
        return False
    return method.lower() in item


def _parse_ambiguity_response(response: str) -> dict[str, Any] | None:
    stripped = response.strip()
    if stripped.startswith("```"):
        parts = stripped.split("```")
        if len(parts) >= 2:
            block = parts[1].lstrip()
            if block.lower().startswith("json"):
                block = block[4:].lstrip()
            stripped = block.strip()
    try:
        data = json.loads(stripped)
    except json.JSONDecodeError:
        start = stripped.find("{")
        end = stripped.rfind("}")
        if start == -1 or end <= start:
            return None
        try:
            data = json.loads(stripped[start : end + 1])
        except json.JSONDecodeError:
            return None
    if not isinstance(data, dict):
        return None
    return data


__all__ = [
    "SchemaAmbiguityGate",
    "SchemaCoverageFinding",
    "SchemaCoverageGate",
]
