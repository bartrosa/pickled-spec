from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pickled_bdd.gates.ambiguity import AmbiguityGate
from pickled_core import Feature, Scenario, Verdict
from pickled_core.cost.models import TokenUsage
from pickled_core.gate import Gate
from pickled_core.llm.base import Completion, LLMClient, Message


class JsonLLMClient(LLMClient):
    provider_key = "json_fake"

    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self._i = 0

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
        _ = messages, max_tokens, temperature, stop, extras
        idx = min(self._i, len(self._responses) - 1)
        r = self._responses[idx]
        self._i += 1
        return Completion(
            text=r,
            usage=TokenUsage(),
            model_id_resolved=model,
            raw_response=None,
        )

    def count_tokens(self, messages: list[Message], model: str) -> int:
        _ = messages, model
        return 1


def _feature(*scenario_names: str) -> Feature:
    scenarios = tuple(
        Scenario(name=n, steps=("Given x", "Then y")) for n in scenario_names
    )
    return Feature(name="F", description="", scenarios=scenarios)


def test_pass_when_all_unambiguous() -> None:
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient([ok, ok, ok]))
    result = gate.run(_feature("S1", "S2", "S3"))
    assert result.verdict == Verdict.PASS
    assert result.findings == ()


def test_warn_when_one_ambiguous() -> None:
    amb = (
        '{"is_ambiguous": true, "alternatives": ["A", "B"], "suggested_fix": "Be specific"}'
    )
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient([amb, ok, ok]))
    result = gate.run(_feature("S1", "S2", "S3"))
    assert result.verdict == Verdict.WARN
    assert len(result.findings) == 1


def test_fail_when_all_ambiguous() -> None:
    amb = (
        '{"is_ambiguous": true, "alternatives": ["A", "B"], "suggested_fix": "Be specific"}'
    )
    gate = AmbiguityGate(JsonLLMClient([amb, amb, amb]))
    result = gate.run(_feature("S1", "S2", "S3"))
    assert result.verdict == Verdict.FAIL


def test_warn_on_parse_errors() -> None:
    gate = AmbiguityGate(JsonLLMClient(["not json", "not json"]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN


def test_strips_markdown_fences() -> None:
    fenced = '```json\n{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}\n```'
    gate = AmbiguityGate(JsonLLMClient([fenced]))
    result = gate.run(_feature("S1"))
    assert result.verdict == Verdict.PASS


def test_gate_protocol() -> None:
    gate = AmbiguityGate(JsonLLMClient(['{"is_ambiguous": false}']))
    assert isinstance(gate, Gate)


def test_partial_parse_errors_warn() -> None:
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient(["%%%", ok]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN


def test_non_feature_target_fails() -> None:
    gate = AmbiguityGate(JsonLLMClient(['{"is_ambiguous": false}']))
    result = gate.run("not a feature")
    assert result.verdict == Verdict.FAIL


def test_parse_error_on_one_scenario_warns() -> None:
    amb = (
        '{"is_ambiguous": true, "alternatives": ["x"], "suggested_fix": "fix"}'
    )
    gate = AmbiguityGate(JsonLLMClient(["bad", amb]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN
