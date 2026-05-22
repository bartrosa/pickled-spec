"""MCP tool registration for pickled-diff."""

from __future__ import annotations

from typing import Any

from pickled_core import PickledMCPServer

from pickled_diff.comparator import ExactEqComparator, StructuralJsonComparator
from pickled_diff.corpus import CorpusItem, InMemoryCorpus
from pickled_diff.gate import DifferentialOracleGate
from pickled_diff.runner import SubprocessRunner
from pickled_diff.types import DifferentialFinding


def _comparator_from_name(name: str) -> ExactEqComparator | StructuralJsonComparator:
    if name == "structural_json":
        return StructuralJsonComparator()
    if name == "exact":
        return ExactEqComparator()
    msg = f"unknown comparator {name!r}; use 'exact' or 'structural_json'"
    raise ValueError(msg)


def register(server: PickledMCPServer) -> None:
    """Register pickled-diff's MCP tools.

    Unlike pickled-bdd, this register() does NOT take an ``llm`` parameter:
    differential verification is deterministic and does not invoke an LLM.
    """

    def verify_against_oracle(
        *,
        oracle_command: list[str],
        candidate_command: list[str],
        corpus_items: list[dict[str, str]],
        comparator: str = "exact",
        timeout_seconds: float = 30.0,
    ) -> dict[str, Any]:
        oracle = SubprocessRunner(
            oracle_command,
            name="oracle",
            timeout_seconds=timeout_seconds,
        )
        candidate = SubprocessRunner(
            candidate_command,
            name="candidate",
            timeout_seconds=timeout_seconds,
        )
        items = [
            CorpusItem(name=str(item["name"]), payload=str(item["payload"]))
            for item in corpus_items
        ]
        corpus = InMemoryCorpus(items)
        gate = DifferentialOracleGate(
            oracle=oracle,
            candidate=candidate,
            comparator=_comparator_from_name(comparator),
        )
        result = gate.run(corpus)
        return {
            "verdict": result.verdict.value,
            "notes": result.notes,
            "findings": [
                {
                    "input_repr": f.input_repr,
                    "oracle_output": f.oracle_output,
                    "candidate_output": f.candidate_output,
                    "diff_summary": f.diff_summary,
                }
                for f in result.findings
                if isinstance(f, DifferentialFinding)
            ],
        }

    server.register_tool(
        "verify_against_oracle",
        verify_against_oracle,
        description=(
            "Compare a candidate command's stdout against a reference oracle command "
            "for each item in an input corpus."
        ),
        input_schema={
            "type": "object",
            "properties": {
                "oracle_command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Argv for the reference implementation subprocess.",
                },
                "candidate_command": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "Argv for the candidate implementation subprocess.",
                },
                "corpus_items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "payload": {"type": "string"},
                        },
                        "required": ["name", "payload"],
                    },
                    "description": "Named inputs passed to stdin for each run.",
                },
                "comparator": {
                    "type": "string",
                    "enum": ["exact", "structural_json"],
                    "default": "exact",
                },
                "timeout_seconds": {
                    "type": "number",
                    "default": 30,
                },
            },
            "required": ["oracle_command", "candidate_command", "corpus_items"],
        },
    )


__all__ = ["register"]
