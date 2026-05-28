"""Tests for mine stories stage."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from pickled_core.cost.models import TokenUsage
from pickled_core.llm.base import Completion, LLMClient, Message
from pickled_core.mine.inventory_stage import collect_adrs_from_dir
from pickled_core.mine.stories_stage import (
    _NO_DOCSTRING_BEHAVIOR,
    _write_one_story,
    collect_surfaces,
    compute_surface_relevant_adrs,
    run_stories,
)

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"
_ADRS_SAMPLE = Path(__file__).resolve().parent / "fixtures" / "adrs_sample"


def test_run_stories_without_llm(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(inv, tmp_path, llm=None, quick=True, overwrite=True)
    assert results
    text = results[0].story_path.read_text(encoding="utf-8")
    assert "## Metadata" in text
    assert "## Context skeleton" not in text
    assert "(LLM unavailable — fill manually)" in text


class _FakeClient(LLMClient):
    provider_key = "fake"

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = model
        return sum(len(m.content) for m in messages)

    def complete(
        self,
        *,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float | None,
        stop: list[str] | None,
        extras: Mapping[str, Any] | None,
    ) -> Completion:
        _ = messages, model, max_tokens, temperature, stop, extras
        return Completion(
            text=(
                "---CONTEXT---\n"
                "Operators use this CLI.\n"
                "---BEHAVIOR---\n"
                "It greets by required name argument.\n"
                "---VERIFY---\n"
                "- greets by name\n"
            ),
            usage=TokenUsage(input=1, output=1),
            model_id_resolved="fake",
            raw_response=None,
        )


def test_run_stories_with_llm(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(inv, tmp_path, llm=_FakeClient(), quick=True, overwrite=True)
    text = results[0].story_path.read_text(encoding="utf-8")
    assert "Operators use this CLI" in text


def test_no_context_skeleton_section(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(inv, tmp_path, llm=None, quick=True, overwrite=True)
    text = results[0].story_path.read_text(encoding="utf-8")
    assert "## Context skeleton" not in text
    assert text.count("## Context") == 1


def test_section_order(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(inv, tmp_path, llm=_FakeClient(), quick=True, overwrite=True)
    text = results[0].story_path.read_text(encoding="utf-8")
    ctx = text.index("## Context")
    today = text.index("## What the target does today")
    verify = text.index("## What we want to verify")
    assert ctx < today < verify


def test_behavior_filled_from_llm_when_docstring_present(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(inv, tmp_path, llm=_FakeClient(), quick=True, overwrite=True)
    text = results[0].story_path.read_text(encoding="utf-8")
    assert "It greets by required name argument" in text


def test_behavior_placeholder_when_no_docstring(tmp_path: Path) -> None:
    data = {
        "packages": {
            "demo": {
                    "cli_commands": [
                        {
                            "full_name": "noop",
                            "help": "",
                            "params": [
                                {
                                    "name": "target",
                                    "required": True,
                                    "help": "",
                                }
                            ],
                            "is_group": False,
                        }
                    ],
                "mcp_tools": [],
                "gates": [],
            }
        },
        "adrs": [],
        "surface_relevant_adrs": {},
    }
    surfaces = collect_surfaces(data)
    assert surfaces
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surfaces[0],
        llm=None,
        overwrite=True,
        interactive=False,
        code_context_dir=None,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert _NO_DOCSTRING_BEHAVIOR in text


def test_relevant_adrs_only(tmp_path: Path) -> None:
    adrs = collect_adrs_from_dir(tmp_path, _ADRS_SAMPLE)
    data = {
        "packages": {
            "pickled-bdd": {
                "cli_commands": [
                    {
                        "full_name": "draft-feature-from-story",
                        "help": (
                            "Draft a Gherkin feature file from an existing user story "
                            "markdown file in the pickled-bdd workflow."
                        ),
                        "params": [],
                        "is_group": False,
                    }
                ],
                "mcp_tools": [],
                "gates": [],
            }
        },
        "adrs": adrs,
    }
    data["surface_relevant_adrs"] = compute_surface_relevant_adrs(data)
    surfaces = collect_surfaces(data)
    bdd = next(s for s in surfaces if s.package == "pickled-bdd")
    titles = {ref.title for ref in bdd.relevant_adrs}
    assert "pickled-diff package" not in titles

    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        bdd,
        llm=None,
        overwrite=True,
        interactive=False,
        code_context_dir=None,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "pickled-diff package" not in text


def test_stories_respects_surfaces_filter(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    results = run_stories(
        inv,
        tmp_path,
        llm=None,
        quick=True,
        overwrite=True,
        surfaces=("tiny",),
    )
    assert results
    for result in results:
        assert "tiny" in result.surface_id


def test_stories_parallel_quick_mode(tmp_path: Path) -> None:
    from pickled_core.mine.inventory_stage import run_inventory

    inv = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    surfaces = collect_surfaces(inv.data)
    assert len(surfaces) >= 2

    one = run_stories(
        inv,
        tmp_path / "p1",
        llm=_FakeClient(),
        quick=True,
        overwrite=True,
        max_parallel=1,
    )
    eight = run_stories(
        inv,
        tmp_path / "p8",
        llm=_FakeClient(),
        quick=True,
        overwrite=True,
        max_parallel=8,
    )
    texts_one = sorted(r.story_path.read_text(encoding="utf-8") for r in one if not r.skipped)
    texts_eight = sorted(r.story_path.read_text(encoding="utf-8") for r in eight if not r.skipped)
    assert texts_one == texts_eight


_CODE_MARKER = "ZEBRA_CODE_BODY_MARKER_42"


def _surface_with_doc(docstring: str) -> object:
    from pickled_core.mine.stories_stage import _Surface

    return _Surface(
        surface_id="demo_surface",
        kind="cli_command",
        package="demo-pkg",
        name="demo run",
        docstring=docstring,
        arguments="- (none)",
        related_gates="(none)",
        relevant_adrs=(),
    )


def _write_code_context(tmp_path: Path, body: str) -> Path:
    code_dir = tmp_path / "code-context"
    code_dir.mkdir()
    (code_dir / "demo_surface.md").write_text(body, encoding="utf-8")
    return code_dir


_CODE_CTX_FILE = f"""# Code context: demo

- **Surface id:** demo_surface
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 20 | **Truncated:** False

## Root: demo_pkg.demo

```python
def run(story: str) -> str:
    return _secret_helper(story)  # line 99
```

## Callee: demo_pkg._secret_helper (hop 1)

```python
def _secret_helper(story: str) -> str:
    # {_CODE_MARKER}
    return story
```

## Unresolved callees

- `self._llm.complete` — protocol or unknown attribute type
"""


class _RecordingClient(LLMClient):
    provider_key = "fake"

    def __init__(self, *, response: str) -> None:
        self.last_prompt = ""
        self._response = response

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = model
        return sum(len(m.content) for m in messages)

    def complete(
        self,
        *,
        messages: list[Message],
        model: str,
        max_tokens: int,
        temperature: float | None,
        stop: list[str] | None,
        extras: Mapping[str, Any] | None,
    ) -> Completion:
        _ = model, max_tokens, temperature, stop, extras
        self.last_prompt = messages[-1].content
        return Completion(
            text=self._response,
            usage=TokenUsage(input=1, output=1),
            model_id_resolved="fake",
            raw_response=None,
        )


def test_story_uses_code_context_when_present(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Claims nothing specific.")
    client = _RecordingClient(
        response=(
            "---CONTEXT---\n"
            "Operators draft features.\n"
            "---BEHAVIOR---\n"
            f"Grounded in {_CODE_MARKER} from code.\n"
            "---VERIFY---\n"
            "- returns story text\n"
            "---DRIFT---\n"
        ),
    )
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    assert _CODE_MARKER in client.last_prompt
    text = result.story_path.read_text(encoding="utf-8")
    assert _CODE_MARKER in text


def test_drift_detected_when_docstring_contradicts_code(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Validates all Gherkin output before returning.")
    client = _RecordingClient(
        response=(
            "---CONTEXT---\n"
            "Draft CLI.\n"
            "---BEHAVIOR---\n"
            "Returns raw text without validation.\n"
            "---VERIFY---\n"
            "- no validation step\n"
            "---DRIFT---\n"
            "- Docstring claims validation; code returns raw text only.\n"
        ),
    )
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "Docstring drift:" in text
    assert "validation" in text.lower()


def test_no_drift_block_when_agreement(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Returns story text unchanged.")
    client = _RecordingClient(
        response=(
            "---CONTEXT---\n"
            "Draft CLI.\n"
            "---BEHAVIOR---\n"
            "Returns story text.\n"
            "---VERIFY---\n"
            "- returns text\n"
            "---DRIFT---\n"
        ),
    )
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "Docstring drift:" not in text


def test_falls_back_to_docstring_only_when_no_code_context(tmp_path: Path) -> None:
    surface = _surface_with_doc("Only from inventory docstring.")
    client = _RecordingClient(
        response=(
            "---CONTEXT---\n"
            "Users.\n"
            "---BEHAVIOR---\n"
            "Only from inventory docstring.\n"
            "---VERIFY---\n"
            "- ok\n"
            "---DRIFT---\n"
            "- should be ignored\n"
        ),
    )
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=None,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "Only from inventory docstring." in text
    assert "Docstring drift:" not in text
    assert "Ground every statement in the provided docstring" in client.last_prompt


def test_no_implementation_leak_in_behavior(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Returns story text.")
    client = _RecordingClient(
        response=(
            "---CONTEXT---\n"
            "Operators.\n"
            "---BEHAVIOR---\n"
            "Accepts a story string and returns the same text without validation.\n"
            "---VERIFY---\n"
            "- returns text\n"
            "---DRIFT---\n"
        ),
    )
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    text = result.story_path.read_text(encoding="utf-8")
    behavior = text.split("## What the target does today", 1)[1].split("##", 1)[0]
    assert "_secret_helper" not in behavior
    assert "line 99" not in behavior


def test_metadata_shows_code_depth_and_unit_counts(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Returns story text.")
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=None,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "**Code depth:** callgraph" in text
    assert "**Units read:** 2" in text
    assert "**Unresolved:** 1" in text


def test_llm_none_summarises_code_context_without_inventing(tmp_path: Path) -> None:
    code_dir = _write_code_context(tmp_path, _CODE_CTX_FILE)
    surface = _surface_with_doc("Validates output.")
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=None,
        overwrite=True,
        interactive=False,
        code_context_dir=code_dir,
    )
    text = result.story_path.read_text(encoding="utf-8")
    assert "LLM unavailable; code-context captured 2 units" in text
    assert "Docstring drift:" not in text
    assert _CODE_MARKER not in text


def test_missing_delimiter_falls_back_with_warning(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    surface = _surface_with_doc("Does something.")
    client = _RecordingClient(response="Unstructured prose only.")
    stories_dir = tmp_path / "stories"
    stories_dir.mkdir()
    result = _write_one_story(
        stories_dir,
        surface,
        llm=client,
        overwrite=True,
        interactive=False,
        code_context_dir=None,
    )
    err = capsys.readouterr().err
    assert "missing delimiters" in err
    text = result.story_path.read_text(encoding="utf-8")
    assert "Unstructured prose only" in text
