from __future__ import annotations

from pickled_bdd.gates.ambiguity import AmbiguityGate
from pickled_core import Feature, Scenario, Verdict
from pickled_core.gate import Gate


class JsonLLMClient:
    def __init__(self, responses: list[str]) -> None:
        self._responses = list(responses)
        self._i = 0

    def complete(
        self,
        prompt: str,
        *,
        system: str | None = None,
    ) -> str:
        _ = prompt, system
        idx = min(self._i, len(self._responses) - 1)
        r = self._responses[idx]
        self._i += 1
        return r


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


def test_warn_when_some_ambiguous() -> None:
    amb = '{"is_ambiguous": true, "alternatives": ["a", "b"], "suggested_fix": "fix"}'
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient([amb, ok, ok]))
    result = gate.run(_feature("S1", "S2", "S3"))
    assert result.verdict == Verdict.WARN
    assert len(result.findings) == 1
    assert result.findings[0].target_name == "S1"


def test_fail_when_all_ambiguous() -> None:
    amb = '{"is_ambiguous": true, "alternatives": ["a"], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient([amb, amb, amb]))
    result = gate.run(_feature("S1", "S2", "S3"))
    assert result.verdict == Verdict.FAIL
    assert len(result.findings) == 3


def test_warn_when_all_responses_unparseable() -> None:
    gate = AmbiguityGate(JsonLLMClient(["not json", "not json"]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN
    assert "Could not parse" in result.notes
    assert "S1" in result.notes or "parse" in result.notes.lower()


def test_fenced_json_parses() -> None:
    fenced = """```json
{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}
```"""
    gate = AmbiguityGate(JsonLLMClient([fenced]))
    result = gate.run(_feature("S1"))
    assert result.verdict == Verdict.PASS


def test_wrong_target_type_fails() -> None:
    gate = AmbiguityGate(JsonLLMClient(['{"is_ambiguous": false}']))
    result = gate.run("not a feature")
    assert result.verdict == Verdict.FAIL
    assert "Feature" in result.notes


def test_parse_error_with_other_ok_warns_and_notes() -> None:
    ok = '{"is_ambiguous": false, "alternatives": [], "suggested_fix": ""}'
    gate = AmbiguityGate(JsonLLMClient(["%%%", ok]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN
    assert "Parse errors" in result.notes


def test_ambiguity_gate_is_gate_protocol() -> None:
    gate = AmbiguityGate(JsonLLMClient(['{"is_ambiguous": false}']))
    assert isinstance(gate, Gate)


def test_malformed_json_skipped_but_other_ambiguous_warns() -> None:
    amb = '{"is_ambiguous": true, "alternatives": ["x"], "suggested_fix": "z"}'
    gate = AmbiguityGate(JsonLLMClient(["bad", amb]))
    result = gate.run(_feature("S1", "S2"))
    assert result.verdict == Verdict.WARN
    assert len(result.findings) == 1
