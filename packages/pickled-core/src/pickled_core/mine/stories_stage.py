"""Stage 2: emit user stories from inventory surfaces."""

from __future__ import annotations

import asyncio
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from pickled_core.llm.base import LLMClient
from pickled_core.llm.prompts import PromptTemplate
from pickled_core.mine.inventory_stage import relevant_adrs_for_surface
from pickled_core.mine.io import (
    ensure_output_dir,
    require_inventory_json,
    surface_matches,
)
from pickled_core.mine.types import InventoryResult, RelevantAdrRef, StoryResult

_PROMPT_PATH = Path(__file__).resolve().parent / "prompts" / "story_from_inventory.md"
_LLM_UNAVAILABLE = "(LLM unavailable — fill manually)"
_NO_DOCSTRING_BEHAVIOR = (
    "The inventory provides no docstring for this surface; behavior must be "
    "confirmed from source before specifying."
)
_SERVE_PLUMBING = frozenset({"serve", "mcp serve"})
_DELIM_CONTEXT = "---CONTEXT---"
_DELIM_BEHAVIOR = "---BEHAVIOR---"
_DELIM_VERIFY = "---VERIFY---"
_DELIM_DRIFT = "---DRIFT---"
_CODE_GROUNDING_WITH_CONTEXT = """\
You are writing a behavioral specification for a code surface. You have:

1. The surface's docstring (what the author CLAIMS it does):
{{docstring}}

2. The actual source code the surface executes (root plus resolved
   intra-project callees), and a list of calls that could not be statically
   resolved:
{{code_context}}

Your job is to describe OBSERVABLE BEHAVIOR — the contract a caller relies
on. Rules:

- Ground every statement in the code. State what the surface accepts,
  returns, rejects, and what side effects a caller observes.
- Describe behavior, NOT implementation. Do NOT mention line numbers,
  private method names, or "it calls X then Y". A reader must understand
  the behavior without seeing the code.
- Where the code reveals behavior the docstring omits (a specific return
  shape, an error mode, the ABSENCE of validation), state it as a
  behavioral fact.
- DOCSTRING DRIFT: if the docstring CONTRADICTS the code (claims a behavior
  the code does not implement, or omits a behavior the code clearly has),
  note the specific discrepancy in the DRIFT block. The code is the source
  of truth; the docstring may be stale.
- Unresolved calls: behavior hidden behind unresolved calls (e.g. a
  protocol-dispatched LLM call) is uncertain. Do NOT invent what those do;
  if a behavior depends on an unresolved call, say it is delegated to an
  unresolved collaborator."""
_CODE_GROUNDING_DOCSTRING_ONLY = """\
Docstring / help from inventory (may be empty):
{{docstring}}

Ground every statement in the provided docstring, arguments, and related
gates. If the docstring is empty or says nothing about behavior, write for
the BEHAVIOR block exactly:

The inventory provides no docstring for this surface; behavior must be
confirmed from source before specifying.

Do NOT infer behavior from the surface's NAME alone. A gate called
AmbiguityGate might do many things; do not assume it detects step-definition
collisions unless the docstring says so.

The DRIFT block must be empty (no code-context to compare against)."""


@dataclass(frozen=True, slots=True)
class CodeContextForStory:
    """Parsed ``code-context/<surface-id>.md`` for story prompts."""

    depth: str
    unit_count: int
    total_lines: int
    unresolved_count: int
    prompt_text: str


@dataclass(frozen=True, slots=True)
class _Surface:
    surface_id: str
    kind: str
    package: str
    name: str
    docstring: str
    arguments: str
    related_gates: str
    relevant_adrs: tuple[RelevantAdrRef, ...]


def _slug_id(raw: str) -> str:
    return re.sub(r"[^a-zA-Z0-9]+", "_", raw).strip("_").lower()


def _surface_id_mcp(tool_name: str) -> str:
    return _slug_id(tool_name)


def _surface_id_cli(package: str, command: str) -> str:
    pkg = _slug_id(package.replace("-", "_"))
    cmd = _slug_id(command.replace(" ", "_"))
    return f"{pkg}_{cmd}"


def _surface_id_gate(package: str, gate_name: str) -> str:
    pkg = _slug_id(package.replace("-", "_"))
    base = gate_name.split(".", 1)[0].lower()
    return f"{pkg}_{_slug_id(base)}"


def _format_relevant_adrs(refs: tuple[RelevantAdrRef, ...]) -> str:
    if not refs:
        return "- (none directly relevant)"
    lines: list[str] = []
    for ref in refs:
        suffix = " (general)" if ref.general else ""
        lines.append(f"- ADR {ref.number}: {ref.title}{suffix} — {ref.status}")
    return "\n".join(lines)


def _load_relevant_adrs(
    data: dict[str, Any],
    *,
    surface_id: str,
    package: str,
    surface_name: str,
) -> tuple[RelevantAdrRef, ...]:
    mapped = data.get("surface_relevant_adrs", {})
    if isinstance(mapped, dict) and surface_id in mapped:
        raw = mapped[surface_id]
        if isinstance(raw, list):
            return tuple(
                RelevantAdrRef(
                    number=str(item.get("number", "")),
                    title=str(item.get("title", "")),
                    status=str(item.get("status", "")),
                    general=bool(item.get("general")),
                )
                for item in raw
                if isinstance(item, dict)
            )
    adrs = data.get("adrs", [])
    if not isinstance(adrs, list):
        return ()
    picked = relevant_adrs_for_surface(
        [a for a in adrs if isinstance(a, dict)],
        package=package,
        surface_id=surface_id,
        surface_name=surface_name,
    )
    return tuple(
        RelevantAdrRef(
            number=str(a.get("number", "")),
            title=str(a.get("title", "")),
            status=str(a.get("status", "")),
            general=bool(a.get("general")),
        )
        for a in picked
    )


def compute_surface_relevant_adrs(data: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    """Build per-surface relevant ADR lists for inventory JSON."""
    result: dict[str, list[dict[str, Any]]] = {}
    for surface in collect_surfaces(data):
        result[surface.surface_id] = [
            {
                "number": ref.number,
                "title": ref.title,
                "status": ref.status,
                "general": ref.general,
            }
            for ref in surface.relevant_adrs
        ]
    return result


def _is_plumbing_cli(full_name: str) -> bool:
    normalized = full_name.strip().lower()
    return normalized in _SERVE_PLUMBING or normalized.endswith(" serve")


def _is_significant_cli(cmd: dict[str, Any]) -> bool:
    if _is_plumbing_cli(str(cmd.get("full_name", ""))):
        return False
    if cmd.get("is_group"):
        return True
    help_text = str(cmd.get("help", ""))
    if len(help_text) > 60:
        return True
    return any(
        isinstance(param, dict) and param.get("required")
        for param in cmd.get("params", [])
    )


def _format_params(params: list[dict[str, Any]]) -> str:
    lines: list[str] = []
    for param in params:
        if not isinstance(param, dict):
            continue
        name = param.get("name", "")
        required = "required" if param.get("required") else "optional"
        help_text = param.get("help", "")
        lines.append(f"- `{name}` ({required}): {help_text}")
    return "\n".join(lines) if lines else "- (none)"


def _gate_docstring(gate: dict[str, Any]) -> str:
    return str(
        gate.get("docstring_summary")
        or gate.get("doc")
        or gate.get("help")
        or ""
    ).strip()


def collect_surfaces(data: dict[str, Any]) -> list[_Surface]:
    surfaces: list[_Surface] = []
    packages = data.get("packages", {})
    if not isinstance(packages, dict):
        return surfaces

    for pkg_name, pkg in packages.items():
        if not isinstance(pkg, dict):
            continue
        gates = pkg.get("gates", [])
        gate_names = [
            str(g.get("name", g.get("class_name", "")))
            for g in gates
            if isinstance(g, dict)
        ]
        gate_block = ", ".join(gate_names) if gate_names else "(none)"

        for tool in pkg.get("mcp_tools", []):
            if not isinstance(tool, dict):
                continue
            name = str(tool.get("name", ""))
            if not name:
                continue
            schema = tool.get("input_schema", {})
            if not isinstance(schema, dict):
                schema = {}
            surface_id = _surface_id_mcp(name)
            surfaces.append(
                _Surface(
                    surface_id=surface_id,
                    kind="mcp_tool",
                    package=str(pkg_name),
                    name=name,
                    docstring=str(tool.get("description", "")).strip(),
                    arguments=_format_params(
                        [
                            {
                                "name": k,
                                "required": k in (schema.get("required") or []),
                                "help": str(v.get("description", "")),
                            }
                            for k, v in (schema.get("properties") or {}).items()
                            if isinstance(v, dict)
                        ]
                    ),
                    related_gates=gate_block,
                    relevant_adrs=_load_relevant_adrs(
                        data,
                        surface_id=surface_id,
                        package=str(pkg_name),
                        surface_name=name,
                    ),
                )
            )

        for cmd in pkg.get("cli_commands", []):
            if not isinstance(cmd, dict) or not _is_significant_cli(cmd):
                continue
            full = str(cmd.get("full_name", ""))
            surface_id = _surface_id_cli(str(pkg_name), full)
            surfaces.append(
                _Surface(
                    surface_id=surface_id,
                    kind="cli_command",
                    package=str(pkg_name),
                    name=full,
                    docstring=str(cmd.get("help", "")).strip(),
                    arguments=_format_params(cmd.get("params", [])),
                    related_gates=gate_block,
                    relevant_adrs=_load_relevant_adrs(
                        data,
                        surface_id=surface_id,
                        package=str(pkg_name),
                        surface_name=full,
                    ),
                )
            )

        for gate in gates:
            if not isinstance(gate, dict):
                continue
            gate_name = str(gate.get("name", gate.get("class_name", "")))
            if not gate_name:
                continue
            surface_id = _surface_id_gate(str(pkg_name), gate_name)
            surfaces.append(
                _Surface(
                    surface_id=surface_id,
                    kind="gate",
                    package=str(pkg_name),
                    name=gate_name,
                    docstring=_gate_docstring(gate),
                    arguments="- (gate class)",
                    related_gates=gate_name,
                    relevant_adrs=_load_relevant_adrs(
                        data,
                        surface_id=surface_id,
                        package=str(pkg_name),
                        surface_name=gate_name,
                    ),
                )
            )
    return surfaces


def parse_code_context_markdown(text: str) -> CodeContextForStory | None:
    """Extract code bodies and metadata from a code-context markdown file."""
    if "No code definition resolved" in text:
        return None
    depth_match = re.search(r"\*\*Depth:\*\*\s*(\w+)", text)
    units_match = re.search(
        r"\*\*Units collected:\*\*\s*(\d+)\s*\|\s*\*\*Total lines:\*\*\s*(\d+)",
        text,
    )
    depth = depth_match.group(1) if depth_match else "body"
    unit_count = int(units_match.group(1)) if units_match else 0
    total_lines = int(units_match.group(2)) if units_match else 0

    parts: list[str] = []
    for match in re.finditer(
        r"## (?:Root: [^\n]+|Callee: [^\n]+)\n\n```python\n(.*?)```",
        text,
        flags=re.DOTALL,
    ):
        parts.append(match.group(1).strip())

    unresolved_lines: list[str] = []
    if "## Unresolved callees" in text:
        section = text.split("## Unresolved callees", 1)[1]
        section = section.split("## ", 1)[0]
        for line in section.splitlines():
            line = line.strip()
            if line.startswith("- `"):
                unresolved_lines.append(line)

    unresolved_count = len(unresolved_lines)
    prompt_parts = ["### Source (root and resolved callees)", ""]
    for idx, source in enumerate(parts, start=1):
        label = "Root" if idx == 1 else f"Unit {idx}"
        prompt_parts.extend([f"#### {label}", "", "```python", source, "```", ""])
    if unresolved_lines:
        prompt_parts.extend(
            [
                "### Unresolved calls (do not invent behavior for these)",
                "",
                *unresolved_lines,
                "",
            ]
        )
    return CodeContextForStory(
        depth=depth,
        unit_count=unit_count,
        total_lines=total_lines,
        unresolved_count=unresolved_count,
        prompt_text="\n".join(prompt_parts).strip(),
    )


def load_code_context_for_surface(
    code_context_dir: Path,
    surface_id: str,
) -> CodeContextForStory | None:
    """Load ``code-context/<surface-id>.md`` when the code stage wrote it."""
    path = code_context_dir / f"{surface_id}.md"
    if not path.is_file():
        return None
    return parse_code_context_markdown(path.read_text(encoding="utf-8"))


def _extract_delimited_block(text: str, start: str, end: str | None) -> str:
    if start not in text:
        return ""
    rest = text.split(start, 1)[1]
    if end and end in rest:
        rest = rest.split(end, 1)[0]
    return rest.strip()


def _parse_llm_blocks(raw: str) -> tuple[str, str, str, str]:
    context = _extract_delimited_block(raw, _DELIM_CONTEXT, _DELIM_BEHAVIOR)
    behavior = _extract_delimited_block(raw, _DELIM_BEHAVIOR, _DELIM_VERIFY)
    verify = _extract_delimited_block(raw, _DELIM_VERIFY, _DELIM_DRIFT)
    drift = _extract_delimited_block(raw, _DELIM_DRIFT, None)
    if not context and not behavior and not verify and not drift and raw.strip():
        context = raw.strip()
    return context, behavior, verify, drift


def _format_drift_open_questions(drift: str) -> str:
    lines: list[str] = []
    for raw in drift.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("- "):
            line = line[2:].strip()
        elif line.startswith("-"):
            line = line[1:].strip()
        if not line.lower().startswith("docstring drift:"):
            line = f"Docstring drift: {line}"
        else:
            line = line[0].upper() + line[1:]
        lines.append(f"- {line}")
    return "\n".join(lines)


def _render_story_body(
    surface: _Surface,
    *,
    context: str,
    behavior: str,
    verify: str,
    open_questions: str = "",
    code_meta: CodeContextForStory | None = None,
) -> str:
    verify_block = verify.strip()
    if verify_block and not verify_block.startswith("-"):
        verify_lines = [f"- {line.strip()}" for line in verify_block.splitlines() if line.strip()]
        verify_block = "\n".join(verify_lines) if verify_lines else "- (none)"
    elif not verify_block:
        verify_block = "- (none)"

    sections = [
        f"# Story: {surface.name}",
        "",
        "## Metadata",
        "",
        f"- **Surface kind:** {surface.kind}",
        f"- **Package:** {surface.package}",
        f"- **Surface id:** {surface.surface_id}",
    ]
    if code_meta is not None:
        sections.append(
            f"- **Code depth:** {code_meta.depth} | **Units read:** "
            f"{code_meta.unit_count} | **Unresolved:** {code_meta.unresolved_count}"
        )
    sections.extend(
        [
            "",
            "## Context",
            "",
            context or _LLM_UNAVAILABLE,
            "",
            "## What the target does today",
            "",
            behavior or _NO_DOCSTRING_BEHAVIOR,
            "",
            "## What we want to verify",
            "",
            verify_block,
            "",
            "## Inventory references",
            "",
            f"- Arguments:\n{surface.arguments}",
            f"- Related gates: {surface.related_gates}",
            f"- Related ADRs:\n{_format_relevant_adrs(surface.relevant_adrs)}",
            "",
            "## Open questions",
            "",
            open_questions,
            "",
            "## Status",
            "",
            "draft",
            "",
        ]
    )
    return "\n".join(sections)


def _code_grounding_block(
    surface: _Surface,
    code_ctx: CodeContextForStory | None,
) -> str:
    doc = surface.docstring or "(none)"
    if code_ctx is None:
        return _CODE_GROUNDING_DOCSTRING_ONLY.replace("{{docstring}}", doc)
    block = _CODE_GROUNDING_WITH_CONTEXT.replace("{{docstring}}", doc)
    return block.replace("{{code_context}}", code_ctx.prompt_text)


def _llm_blocks_for_surface(
    surface: _Surface,
    llm: LLMClient,
    *,
    code_ctx: CodeContextForStory | None,
) -> tuple[str, str, str, str]:
    template = PromptTemplate.from_file(_PROMPT_PATH)
    prompt = template.render(
        surface_name=surface.name,
        surface_kind=surface.kind,
        package_name=surface.package,
        code_grounding_block=_code_grounding_block(surface, code_ctx),
        arguments=surface.arguments,
        related_gates=surface.related_gates,
        related_adrs=_format_relevant_adrs(surface.relevant_adrs),
    )
    from pickled_core.llm.turns import complete_prompt

    raw = complete_prompt(
        llm,
        prompt,
        system="You output only the four delimiter blocks requested.",
    ).strip()
    context, behavior, verify, drift = _parse_llm_blocks(raw)
    missing = []
    if not context:
        missing.append("CONTEXT")
    if not behavior:
        missing.append("BEHAVIOR")
    if not verify:
        missing.append("VERIFY")
    if missing:
        sys.stderr.write(
            f"[WARN] LLM story for {surface.surface_id} missing delimiters: "
            f"{', '.join(missing)}\n"
        )
    if not behavior and surface.docstring and code_ctx is None:
        behavior = surface.docstring
    elif not behavior:
        behavior = _NO_DOCSTRING_BEHAVIOR
    if not context:
        context = _LLM_UNAVAILABLE
    if not verify:
        verify = _LLM_UNAVAILABLE
    if code_ctx is None:
        drift = ""
    return context, behavior, verify, drift


def _deterministic_blocks(
    surface: _Surface,
    *,
    code_ctx: CodeContextForStory | None,
) -> tuple[str, str, str, str]:
    context = _LLM_UNAVAILABLE
    if code_ctx is not None:
        behavior = (
            f"(LLM unavailable; code-context captured {code_ctx.unit_count} units, "
            f"{code_ctx.total_lines} lines — see code-context/{surface.surface_id}.md)"
        )
    else:
        behavior = surface.docstring or _NO_DOCSTRING_BEHAVIOR
    verify = _LLM_UNAVAILABLE
    return context, behavior, verify, ""


def _write_one_story(
    paths_stories_dir: Path,
    surface: _Surface,
    *,
    llm: LLMClient | None,
    overwrite: bool,
    interactive: bool,
    code_context_dir: Path | None,
) -> StoryResult:
    story_path = paths_stories_dir / f"{surface.surface_id}.story.md"
    if (
        story_path.is_file()
        and story_path.read_text(encoding="utf-8").strip()
        and not overwrite
    ):
        return StoryResult(
            surface_id=surface.surface_id,
            story_path=story_path,
            skipped=True,
        )

    code_ctx: CodeContextForStory | None = None
    if code_context_dir is not None:
        code_ctx = load_code_context_for_surface(code_context_dir, surface.surface_id)

    open_questions = ""
    drift = ""
    if llm is None:
        context, behavior, verify, drift = _deterministic_blocks(
            surface, code_ctx=code_ctx
        )
    else:
        try:
            context, behavior, verify, drift = _llm_blocks_for_surface(
                surface, llm, code_ctx=code_ctx
            )
        except Exception as exc:
            sys.stderr.write(
                f"[WARN] LLM story draft failed for {surface.surface_id}: "
                f"{type(exc).__name__}: {exc}\n"
            )
            context, behavior, verify, drift = _deterministic_blocks(
                surface, code_ctx=code_ctx
            )

    drift_questions = _format_drift_open_questions(drift)
    if interactive and llm is not None:
        open_questions = input(
            f"Open questions for {surface.surface_id} (or leave blank): "
        ).strip()

    combined_open = "\n".join(
        part for part in (drift_questions, open_questions) if part.strip()
    )

    body = _render_story_body(
        surface,
        context=context,
        behavior=behavior,
        verify=verify,
        open_questions=combined_open or "(none)",
        code_meta=code_ctx,
    )
    story_path.write_text(body, encoding="utf-8")
    return StoryResult(
        surface_id=surface.surface_id,
        story_path=story_path,
        skipped=False,
    )


async def _write_one_story_async(
    paths_stories_dir: Path,
    surface: _Surface,
    llm: LLMClient,
    *,
    overwrite: bool,
    sem: asyncio.Semaphore,
    code_context_dir: Path | None,
) -> StoryResult:
    async with sem:
        return await asyncio.to_thread(
            _write_one_story,
            paths_stories_dir,
            surface,
            llm=llm,
            overwrite=overwrite,
            interactive=False,
            code_context_dir=code_context_dir,
        )


def run_stories(
    inventory: InventoryResult,
    output_dir: Path,
    *,
    llm: LLMClient | None,
    quick: bool,
    overwrite: bool,
    surfaces: tuple[str, ...] = (),
    max_parallel: int = 4,
    code_context_dir: Path | None = None,
) -> list[StoryResult]:
    """Write one ``.story.md`` per significant inventory surface."""
    paths = ensure_output_dir(output_dir)
    ctx_dir = code_context_dir
    if ctx_dir is None and paths.code_context_dir.is_dir():
        ctx_dir = paths.code_context_dir
    all_surfaces = collect_surfaces(inventory.data)
    selected = [
        s
        for s in all_surfaces
        if surface_matches(
            surface_id=s.surface_id,
            package=s.package,
            tokens=surfaces,
        )
    ]
    selected.sort(key=lambda s: s.surface_id)

    if not quick or llm is None:
        return [
            _write_one_story(
                paths.stories_dir,
                surface,
                llm=llm,
                overwrite=overwrite,
                interactive=not quick and llm is not None,
                code_context_dir=ctx_dir,
            )
            for surface in selected
        ]

    sem = asyncio.Semaphore(max_parallel)

    async def _run() -> list[StoryResult]:
        tasks = [
            _write_one_story_async(
                paths.stories_dir,
                surface,
                llm,
                overwrite=overwrite,
                sem=sem,
                code_context_dir=ctx_dir,
            )
            for surface in selected
        ]
        gathered = await asyncio.gather(*tasks)
        return sorted(gathered, key=lambda r: r.surface_id)

    return asyncio.run(_run())


def load_inventory_from_output(output_dir: Path) -> InventoryResult:
    """Load ``inventory.json`` produced by a prior inventory stage."""
    paths = ensure_output_dir(output_dir)
    data = require_inventory_json(output_dir, needed_by="stories")
    warnings = data.get("warnings", []) if isinstance(data.get("warnings"), list) else []
    return InventoryResult(
        inventory_path=paths.inventory_json,
        data=data,
        warnings=[str(w) for w in warnings],
    )


__all__ = [
    "CodeContextForStory",
    "collect_surfaces",
    "compute_surface_relevant_adrs",
    "load_code_context_for_surface",
    "load_inventory_from_output",
    "parse_code_context_markdown",
    "run_stories",
]
