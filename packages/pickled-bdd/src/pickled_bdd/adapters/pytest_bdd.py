"""pytest-bdd adapter — parses `.feature` files via gherkin-official.

At parse time we **prepend Background steps to every Scenario**, matching what
pytest-bdd does at runtime, so downstream gates see the full executable step
sequence.

Feature-level tags are inherited by every scenario in the feature, matching
pytest-bdd's runtime behaviour (feature tags become pytest marks on every
scenario test). This is critical for downstream gates such as the
``pickled-rules`` coverage gate, which derives rule references from scenario
tags: a feature tagged ``@team-api-conv:naming.1`` must report ``naming.1``
referenced for every scenario in the file, otherwise the gate may emit a
false FAIL verdict.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, cast

from gherkin.parser import Parser
from gherkin.token_scanner import TokenScanner
from pickled_core import Feature, Scenario


class PytestBddAdapter:
    """Adapter for the pytest-bdd runner.

    v0.1 implements parsing only. Programmatic test execution and
    step-binding generation land in later PRs.
    """

    name = "pytest-bdd"

    def parse_feature_file(self, path: str | Path) -> Feature:
        """Parse a `.feature` file into a runner-agnostic Feature.

        Handles Scenario, Scenario Outline, Examples, Background, and
        Rule blocks. Background steps are prepended to every scenario
        in the feature (the same expansion pytest-bdd performs at
        runtime); rule-level Background steps are appended after the
        feature-level Background for scenarios inside that rule.
        """
        p = Path(path)
        text = p.read_text(encoding="utf-8")
        ast = cast(dict[str, Any], Parser().parse(TokenScanner(text)))
        return self._build_feature(ast, path=str(p))

    def _build_feature(self, ast: dict[str, Any], *, path: str) -> Feature:
        feature_node = ast.get("feature") or {}
        name = feature_node.get("name", "")
        raw_desc = feature_node.get("description") or ""
        description = "\n".join(line.strip() for line in raw_desc.splitlines()).strip()

        feature_tags = self._extract_tags(feature_node)
        background_steps: tuple[str, ...] = ()
        scenarios: list[Scenario] = []

        for child in feature_node.get("children", []):
            if "background" in child:
                background_steps = self._extract_steps(child["background"])
            elif "scenario" in child:
                scenarios.extend(
                    self._expand_scenario(child["scenario"], background_steps)
                )
            elif "rule" in child:
                scenarios.extend(
                    self._expand_rule(child["rule"], background_steps)
                )

        if feature_tags:
            scenarios = [
                Scenario(
                    name=s.name,
                    steps=s.steps,
                    tags=feature_tags + tuple(t for t in s.tags if t not in feature_tags),
                    line=s.line,
                )
                for s in scenarios
            ]

        return Feature(
            name=name,
            description=description,
            scenarios=tuple(scenarios),
            path=path,
        )

    def _expand_rule(
        self,
        rule_node: dict[str, Any],
        feature_background: tuple[str, ...],
    ) -> list[Scenario]:
        """Flatten a ``Rule:`` block into a list of scenarios.

        Rule-level Background is appended after the feature-level
        Background. Rule-level tags are inherited by each scenario inside
        the rule, matching pytest-bdd's runtime behaviour.
        """
        rule_background: tuple[str, ...] = ()
        rule_tags = self._extract_tags(rule_node)
        out: list[Scenario] = []

        for child in rule_node.get("children", []):
            if "background" in child:
                rule_background = self._extract_steps(child["background"])
            elif "scenario" in child:
                combined_background = feature_background + rule_background
                expanded = self._expand_scenario(child["scenario"], combined_background)
                if rule_tags:
                    out.extend(
                        Scenario(
                            name=s.name,
                            steps=s.steps,
                            tags=tuple(rule_tags) + tuple(s.tags),
                            line=s.line,
                        )
                        for s in expanded
                    )
                else:
                    out.extend(expanded)
        return out

    def _extract_steps(self, node: dict[str, Any]) -> tuple[str, ...]:
        steps: list[str] = []
        for step in node.get("steps", []):
            keyword = step.get("keyword", "").strip()
            text = step.get("text", "").strip()
            steps.append(f"{keyword} {text}".strip())
        return tuple(steps)

    def _extract_tags(self, node: dict[str, Any]) -> tuple[str, ...]:
        return tuple(t["name"].lstrip("@") for t in node.get("tags", []))

    def _expand_scenario(
        self,
        node: dict[str, Any],
        background_steps: tuple[str, ...],
    ) -> list[Scenario]:
        """Expand a scenario node into one or more `Scenario` objects.

        A plain `Scenario` becomes one Scenario. A `Scenario Outline`
        with N rows in `Examples` becomes N Scenarios.
        """
        scenario_steps = self._extract_steps(node)
        base_steps = background_steps + scenario_steps
        tags = self._extract_tags(node)
        line = int(node.get("location", {}).get("line", 0))
        scenario_name = node.get("name", "")

        examples = node.get("examples") or []
        if not examples:
            return [
                Scenario(
                    name=scenario_name,
                    steps=base_steps,
                    tags=tags,
                    line=line,
                )
            ]

        result: list[Scenario] = []
        for example_block in examples:
            header_cells = (example_block.get("tableHeader") or {}).get("cells", [])
            header = [cell["value"] for cell in header_cells]
            for row in example_block.get("tableBody", []):
                values = [cell["value"] for cell in row.get("cells", [])]
                row_map = dict(zip(header, values, strict=True))
                expanded_steps = tuple(
                    self._substitute(step, row_map) for step in base_steps
                )
                result.append(
                    Scenario(
                        name=scenario_name,
                        steps=expanded_steps,
                        tags=tags,
                        line=line,
                    )
                )
        return result

    @staticmethod
    def _substitute(step: str, mapping: dict[str, str]) -> str:
        for key, value in mapping.items():
            step = step.replace(f"<{key}>", value)
        return step
