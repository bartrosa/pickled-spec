from __future__ import annotations

from pickled_core import Verdict
from pickled_iac.gates import PlanDiffGate


def test_plan_diff_pass_when_no_changes(empty_plan: dict) -> None:
    result = PlanDiffGate().run(empty_plan, context={"base_plan": empty_plan})
    assert result.verdict is Verdict.PASS


def test_plan_diff_warn_on_create_only(empty_plan: dict, create_plan: dict) -> None:
    result = PlanDiffGate().run(create_plan, context={"base_plan": empty_plan})
    assert result.verdict is Verdict.WARN
    assert len(result.findings) >= 1


def test_plan_diff_fail_on_delete(empty_plan: dict, delete_plan: dict) -> None:
    result = PlanDiffGate().run(delete_plan, context={"base_plan": empty_plan})
    assert result.verdict is Verdict.FAIL
