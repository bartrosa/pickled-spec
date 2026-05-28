"""Tests for mine inventory stage."""

from __future__ import annotations

import ast
import textwrap
from pathlib import Path

from pickled_core.mine.inventory_stage import (
    collect_adrs_from_dir,
    enrich_inventory_data,
    parse_adr_file,
    relevant_adrs_for_surface,
    run_inventory,
)

_FIXTURE = Path(__file__).resolve().parent / "fixtures" / "tiny_target"
_ADRS_SAMPLE = Path(__file__).resolve().parent / "fixtures" / "adrs_sample"


def test_run_inventory_tiny_target(tmp_path: Path) -> None:
    result = run_inventory(_FIXTURE, tmp_path, include_mcp=False, verbose=False)
    assert result.inventory_path.is_file()
    data = result.data
    assert data["totals"]["cli_commands"] >= 2
    assert "tiny-target" in data["packages"]
    commands = data["packages"]["tiny-target"]["cli_commands"]
    names = {c["full_name"] for c in commands}
    assert "greet" in names
    assert "ping" in names


def test_inventory_skips_mcp_without_pickled_spec(tmp_path: Path) -> None:
    plain = tmp_path / "plain"
    plain.mkdir()
    (plain / "pyproject.toml").write_text(
        '[project]\nname = "plain"\nversion = "0.0.1"\n',
        encoding="utf-8",
    )
    result = run_inventory(plain, tmp_path / "out", include_mcp=True, verbose=False)
    assert result.data["totals"]["mcp_tools"] == 0
    assert any("umbrella MCP" in w for w in result.warnings)


def test_adr_title_strips_number_prefix(tmp_path: Path) -> None:
    adr_path = _ADRS_SAMPLE / "0001-pickled-diff-package.md"
    parsed = parse_adr_file(tmp_path, adr_path)
    assert parsed["title"] == "pickled-diff package"
    assert "ADR-0001:" not in parsed["title"]


def test_adr_status_parsed_accepted_proposed_superseded(tmp_path: Path) -> None:
    adrs = collect_adrs_from_dir(tmp_path, _ADRS_SAMPLE)
    by_number = {a["number"]: a for a in adrs}
    assert by_number["0001"]["status"] == "Accepted"
    assert by_number["0002"]["status"] == "Proposed"
    assert by_number["0003"]["status"] == "Superseded"


def test_gate_class_docstring_extracted(tmp_path: Path) -> None:
    gate_file = tmp_path / "gates" / "sample_gate.py"
    gate_file.parent.mkdir(parents=True)
    gate_file.write_text(
        textwrap.dedent(
            '''
            """Module gates."""

            class SampleGate:
                """Class-level gate purpose."""

                def run(self, target: object) -> GateResult:
                    """Method-level fallback."""
                    ...
            '''
        ),
        encoding="utf-8",
    )
    tree = ast.parse(gate_file.read_text(encoding="utf-8"))
    class_node = next(n for n in tree.body if isinstance(n, ast.ClassDef))
    method_node = next(
        n
        for n in class_node.body
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == "run"
    )

    from pickled_core.mine.inventory_stage import _first_paragraph_docstring

    assert "Class-level gate purpose" in _first_paragraph_docstring(class_node)
    assert "Method-level fallback" in _first_paragraph_docstring(method_node)

    data = {
        "packages": {
            "demo": {
                "gates": [
                    {
                        "kind": "class",
                        "name": "SampleGate.run",
                        "file": "gates/sample_gate.py",
                    }
                ]
            }
        },
        "adrs": [],
    }
    enrich_inventory_data(data, tmp_path)
    gate = data["packages"]["demo"]["gates"][0]
    assert gate["docstring_summary"] == "Class-level gate purpose."


def test_gate_class_falls_back_to_method_docstring(tmp_path: Path) -> None:
    gate_file = tmp_path / "gates" / "no_class_doc.py"
    gate_file.parent.mkdir(parents=True)
    gate_file.write_text(
        textwrap.dedent(
            '''
            class BareGate:
                def run(self, target: object) -> GateResult:
                    """Only the run method is documented."""
                    ...
            '''
        ),
        encoding="utf-8",
    )
    data = {
        "packages": {
            "demo": {
                "gates": [
                    {
                        "kind": "class",
                        "name": "BareGate.run",
                        "file": "gates/no_class_doc.py",
                    }
                ]
            }
        },
        "adrs": [],
    }
    enrich_inventory_data(data, tmp_path)
    gate = data["packages"]["demo"]["gates"][0]
    assert "Only the run method is documented" in gate["docstring_summary"]


def test_adr_relevance_filters_unrelated() -> None:
    adrs = collect_adrs_from_dir(Path("/tmp"), _ADRS_SAMPLE)
    bdd_refs = relevant_adrs_for_surface(
        adrs,
        package="pickled-bdd",
        surface_id="pickled_bdd_draft_feature",
        surface_name="bdd_draft_feature_from_story",
    )
    titles = {r["title"] for r in bdd_refs}
    assert "pickled-diff package" not in titles

    cache_refs = relevant_adrs_for_surface(
        adrs,
        package="pickled-core",
        surface_id="core_llm_cache",
        surface_name="cache",
    )
    cache_titles = {r["title"] for r in cache_refs}
    assert any("cache" in t.lower() for t in cache_titles)
