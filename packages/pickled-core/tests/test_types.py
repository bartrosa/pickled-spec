from __future__ import annotations

from pickled_core import Feature, Scenario, Verdict


def test_verdict_pass_value() -> None:
    assert Verdict.PASS.value == "pass"


def test_verdict_string_enum_compare() -> None:
    assert Verdict.PASS == "pass"
    assert Verdict.WARN == "warn"
    assert Verdict.FAIL == "fail"


def test_scenario_is_hashable() -> None:
    s = Scenario(name="Login", steps=("Given x", "Then y"), tags=("smoke",), line=10)
    assert hash(s) == hash(s)
    assert {s: 1}[s] == 1


def test_feature_round_trip() -> None:
    sc = Scenario(name="S1", steps=("Given a",))
    f = Feature(
        name="Auth",
        description="Login flow",
        scenarios=(sc,),
        path="features/auth.feature",
    )
    assert f.name == "Auth"
    assert f.description == "Login flow"
    assert f.path == "features/auth.feature"
    assert len(f.scenarios) == 1
    assert f.scenarios[0].name == "S1"
    assert isinstance(f.scenarios, tuple)
