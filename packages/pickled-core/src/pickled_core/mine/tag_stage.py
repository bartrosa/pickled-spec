"""Stage 4: propose scenario tags from rule sets."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml
from pickled_rules.gates_runner import _resolve_ruleset_entries
from pickled_rules.loader import RuleSetValidationError, load_ruleset
from pickled_rules.types import Rule

from pickled_core.mine.io import (
    ensure_output_dir,
    require_features_dir,
    surface_matches,
    write_json,
)
from pickled_core.mine.types import (
    LoadedRulesetEntry,
    RulesetSources,
    TagProposal,
    TagResult,
)

_SCENARIO_LINE = re.compile(
    r"^(\s*)(Scenario(?: Outline| Template)?):\s*.+$",
)
_TAG_LINE = re.compile(r"^\s*(@\S+)\s*$")
# Repair legacy corruption from character-offset injection (pre friction #16).
_BROKEN_SCENARIO_TAG = re.compile(
    r"^(\s*)Sc\w*(@\S+)\n(?:enario|rio|io)?(:.*)$",
    re.MULTILINE | re.IGNORECASE,
)
_TOKEN_RE = re.compile(r"[a-z0-9]+")
_PREFERRED_SHORT = frozenset({"pickled-internal", "best-practices"})
_STOP = frozenset(
    {
        "a",
        "an",
        "the",
        "and",
        "or",
        "to",
        "of",
        "in",
        "on",
        "for",
        "is",
        "are",
        "be",
        "when",
        "then",
        "given",
        "with",
        "that",
        "this",
        "as",
        "at",
        "by",
        "from",
        "it",
        "not",
    }
)


def _tokenize(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall(text.lower()) if len(t) > 2 and t not in _STOP}


def _rule_weight(short_name: str, package_hint: str) -> int:
    lower = short_name.lower()
    if package_hint and package_hint in lower:
        return 3
    if lower in _PREFERRED_SHORT:
        return 2
    return 1


def _score_rule(
    rule: Rule,
    *,
    short_name: str,
    package_hint: str,
    step_tokens: set[str],
) -> int:
    title_tokens = _tokenize(rule.title)
    overlap = len(step_tokens & title_tokens)
    if overlap == 0:
        return 0
    return overlap * _rule_weight(short_name, package_hint)


def _propose_for_text(
    text: str,
    loaded: list[LoadedRulesetEntry],
    *,
    package_hint: str,
    known_rule_ids: set[str],
) -> list[TagProposal]:
    step_tokens = _tokenize(text)
    scored: list[tuple[int, TagProposal]] = []
    for entry in loaded:
        for rule in entry.ruleset.rules:
            score = _score_rule(
                rule,
                short_name=entry.short_name,
                package_hint=package_hint,
                step_tokens=step_tokens,
            )
            if score <= 0:
                continue
            tag = f"@{entry.short_name}:{rule.id}"
            if rule.id not in known_rule_ids:
                continue
            scored.append(
                (
                    score,
                    TagProposal(
                        tag=tag,
                        rule_id=rule.id,
                        short_name=entry.short_name,
                        rule_title=rule.title,
                        score=score,
                    ),
                )
            )
    scored.sort(key=lambda item: (-item[0], item[1].tag))
    seen: set[str] = set()
    proposals: list[TagProposal] = []
    for _, proposal in scored:
        if proposal.tag in seen:
            continue
        seen.add(proposal.tag)
        proposals.append(proposal)
        if len(proposals) >= 7:
            break
    return proposals


def _package_hint_from_feature(path: Path) -> str:
    stem = path.stem.replace("-", "_").lower()
    return stem.split("_", 1)[0] if "_" in stem else stem


def _known_rule_ids(loaded: list[LoadedRulesetEntry]) -> set[str]:
    ids: set[str] = set()
    for entry in loaded:
        ids.update(rule.id for rule in entry.ruleset.rules)
    return ids


def resolve_ruleset_sources(
    target: Path,
    *,
    ruleset_config: Path | None,
    ruleset_dir: Path | None,
) -> RulesetSources | None:
    """Resolve rule sets from CLI flags or target-root config."""
    if ruleset_config is not None:
        cfg_path = ruleset_config.resolve()
        if not cfg_path.is_file():
            msg = f"ruleset config not found: {cfg_path}"
            raise FileNotFoundError(msg)
        cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
        if not isinstance(cfg, dict):
            msg = f"invalid ruleset config: {cfg_path}"
            raise RuleSetValidationError(msg)
        root = cfg_path.parent
        entries = _resolve_ruleset_entries(root, cfg)
        return _load_entries(entries, config_root=root)

    if ruleset_dir is not None:
        root = ruleset_dir.resolve()
        if not root.is_dir():
            msg = f"ruleset dir not found: {root}"
            raise FileNotFoundError(msg)
        loaded = [
            LoadedRulesetEntry(
                short_name=path.stem,
                path=path,
                ruleset=load_ruleset(path),
            )
            for path in sorted(root.glob("*.yaml"))
        ]
        return RulesetSources(config_root=root, rulesets=loaded)

    cfg_path = target.resolve() / "pickled.ruleset.yaml"
    if not cfg_path.is_file():
        return None
    cfg = yaml.safe_load(cfg_path.read_text(encoding="utf-8"))
    if not isinstance(cfg, dict):
        return None
    root = cfg_path.parent
    entries = _resolve_ruleset_entries(root, cfg)
    if not entries:
        return None
    return _load_entries(entries, config_root=root)


def _load_entries(
    entries: list[Any],  # pickled_rules.gates_runner._RulesetEntry
    *,
    config_root: Path,
) -> RulesetSources:
    loaded: list[LoadedRulesetEntry] = []
    for entry in entries:
        loaded.append(
            LoadedRulesetEntry(
                short_name=entry.short_name,
                path=entry.path,
                ruleset=load_ruleset(entry.path),
            )
        )
    return RulesetSources(config_root=config_root, rulesets=loaded)


def _repair_split_scenario_tags(feature_text: str) -> str:
    """Fix tag lines spliced into the middle of ``Scenario`` from legacy offset injection."""

    def repl(match: re.Match[str]) -> str:
        indent, tag, title_rest = match.groups()
        return f"{indent}{tag}\n{indent}Scenario{title_rest}"

    repaired = feature_text
    for _ in range(8):
        next_text = _BROKEN_SCENARIO_TAG.sub(repl, repaired)
        if next_text == repaired:
            break
        repaired = next_text

    lines = repaired.splitlines()
    fixed_lines: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        split_head = re.match(r"^(\s*)Sc\w*(@\S+)\s*$", line)
        if split_head is not None and index + 1 < len(lines):
            tail = lines[index + 1]
            tail_match = re.match(
                r"^(enario|ario|rio|io)(:.*)$",
                tail.strip(),
                re.IGNORECASE,
            )
            if tail_match is not None:
                indent, tag = split_head.groups()
                fixed_lines.append(f"{indent}{tag}")
                fixed_lines.append(f"{indent}Scenario{tail_match.group(2)}")
                index += 2
                continue
        fixed_lines.append(line)
        index += 1
    return "\n".join(fixed_lines) + ("\n" if feature_text.endswith("\n") else "")


def _tags_immediately_above(lines: list[str], scenario_line_index: int) -> set[str]:
    tags: set[str] = set()
    index = scenario_line_index - 1
    while index >= 0:
        line = lines[index]
        if not line.strip():
            break
        match = _TAG_LINE.match(line)
        if match is None:
            break
        tags.add(match.group(1))
        index -= 1
    return tags


def _scenario_line_spans(lines: list[str]) -> list[tuple[int, str, str]]:
    """Return ``(line_index, indent, full_scenario_line)`` for each scenario header."""
    spans: list[tuple[int, str, str]] = []
    for index, line in enumerate(lines):
        match = _SCENARIO_LINE.match(line)
        if match is not None:
            spans.append((index, match.group(1), line))
    return spans


def _scenario_blocks_from_lines(
    lines: list[str],
) -> list[tuple[int, str, str]]:
    """Return ``(scenario_line_index, block_text, scenario_title)`` per scenario."""
    spans = _scenario_line_spans(lines)
    blocks: list[tuple[int, str, str]] = []
    for idx, (line_index, _indent, title_line) in enumerate(spans):
        end_line = spans[idx + 1][0] if idx + 1 < len(spans) else len(lines)
        block_text = "\n".join(lines[line_index:end_line])
        blocks.append((line_index, block_text, title_line.strip()))
    return blocks


def apply_line_based_tags(
    feature_text: str,
    scenario_tags: list[tuple[int, list[str]]],
) -> str:
    """Insert tag lines immediately above each scenario line (line-based, never in-line)."""
    trailing_newline = feature_text.endswith("\n")
    lines = feature_text.splitlines()

    for line_index, tags in sorted(scenario_tags, key=lambda item: item[0], reverse=True):
        if line_index < 0 or line_index >= len(lines):
            continue
        if _SCENARIO_LINE.match(lines[line_index]) is None:
            continue
        indent_match = re.match(r"^(\s*)", lines[line_index])
        indent = indent_match.group(1) if indent_match else ""
        existing = _tags_immediately_above(lines, line_index)
        new_tag_lines: list[str] = []
        seen_new: set[str] = set()
        for tag in tags:
            if tag in existing or tag in seen_new:
                continue
            seen_new.add(tag)
            new_tag_lines.append(f"{indent}{tag}")
        if not new_tag_lines:
            continue
        lines[line_index:line_index] = new_tag_lines

    result = "\n".join(lines)
    if trailing_newline and not result.endswith("\n"):
        result += "\n"
    return result


def _filter_feature_paths(
    feature_paths: list[Path],
    surfaces: tuple[str, ...],
) -> list[Path]:
    if not surfaces:
        return feature_paths
    filtered: list[Path] = []
    for path in feature_paths:
        surface_id = path.stem
        package = _package_hint_from_feature(path)
        if surface_matches(surface_id=surface_id, package=package, tokens=surfaces):
            filtered.append(path)
    return filtered


def run_tag(
    output_dir: Path,
    *,
    ruleset_sources: RulesetSources | None,
    quick: bool,
    surfaces: tuple[str, ...] = (),
) -> TagResult:
    """Propose tags for scenarios in generated features."""
    paths = ensure_output_dir(output_dir)
    if ruleset_sources is None:
        sys.stderr.write("[WARN] no rule sets configured; tagging skipped\n")
        return TagResult(
            proposals_path=paths.tags_proposals,
            proposals=[],
            skipped=True,
            warnings=["no rule sets configured; tagging skipped"],
        )

    features_dir = require_features_dir(output_dir, needed_by="tag")
    feature_paths = _filter_feature_paths(
        sorted(features_dir.glob("*.feature")),
        surfaces,
    )
    if not feature_paths:
        msg = "no features match --surfaces filter"
        raise ValueError(msg)

    loaded = ruleset_sources.rulesets
    known_ids = _known_rule_ids(loaded)
    document: dict[str, Any] = {"schema_version": "1", "features": []}
    all_proposals: list[dict[str, Any]] = []

    for feature_path in feature_paths:
        raw_text = feature_path.read_text(encoding="utf-8")
        text = _repair_split_scenario_tags(raw_text)
        package_hint = _package_hint_from_feature(feature_path)
        lines = text.splitlines()
        feature_entry: dict[str, Any] = {
            "feature_path": str(feature_path.relative_to(paths.root)),
            "scenarios": [],
        }
        injections: list[tuple[int, list[str]]] = []

        for line_index, block, title in _scenario_blocks_from_lines(lines):
            proposals = _propose_for_text(
                block,
                loaded,
                package_hint=package_hint,
                known_rule_ids=known_ids,
            )
            proposal_dicts = [
                {
                    "tag": p.tag,
                    "rule_id": p.rule_id,
                    "short_name": p.short_name,
                    "rule_title": p.rule_title,
                    "score": p.score,
                }
                for p in proposals
            ]
            selected: str | None = None
            tags_for_scenario: list[str] = []

            if proposals and quick:
                selected = proposals[0].tag
                tags_for_scenario = [selected]
            elif proposals and not quick:
                sys.stderr.write(f"\n{feature_path.name} — {title}\n")
                for idx, proposal in enumerate(proposals, start=1):
                    sys.stderr.write(
                        f"  {idx}. {proposal.tag} ({proposal.score}) — {proposal.rule_title}\n"
                    )
                choice = input("tag number, custom @short:id, or skip: ").strip()
                if choice.isdigit():
                    pick = int(choice) - 1
                    if 0 <= pick < len(proposals):
                        selected = proposals[pick].tag
                        tags_for_scenario = [selected]
                elif choice.startswith("@"):
                    selected = choice
                    tags_for_scenario = [selected]

            if tags_for_scenario:
                injections.append((line_index, tags_for_scenario))

            feature_entry["scenarios"].append(
                {
                    "scenario_title": title,
                    "proposals": proposal_dicts,
                    "selected": selected,
                }
            )
            all_proposals.extend(proposal_dicts)

        updated = apply_line_based_tags(text, injections)
        if updated != raw_text:
            feature_path.write_text(updated, encoding="utf-8")
        document["features"].append(feature_entry)

    write_json(paths.tags_proposals, document)
    return TagResult(
        proposals_path=paths.tags_proposals,
        proposals=all_proposals,
        skipped=False,
    )


__all__ = [
    "apply_line_based_tags",
    "resolve_ruleset_sources",
    "repair_split_scenario_tags",
    "run_tag",
]

# Public alias for tests and migration tooling.
repair_split_scenario_tags = _repair_split_scenario_tags
