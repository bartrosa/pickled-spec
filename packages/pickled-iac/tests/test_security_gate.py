from __future__ import annotations

import shutil

import pytest
from pickled_core import Verdict
from pickled_iac.gates import SecurityBaselineGate

TRIVY = shutil.which("trivy")


def test_security_gate_skips_when_trivy_missing(users_rds_dir) -> None:
    if TRIVY:
        pytest.skip("trivy present — use test with fixture")
    result = SecurityBaselineGate().run(users_rds_dir)
    assert result.verdict is Verdict.PASS
    assert "skipped" in result.notes.lower()


@pytest.mark.skipif(TRIVY is None, reason="trivy not on PATH")
def test_security_gate_fails_on_insecure_s3(insecure_s3_dir) -> None:
    result = SecurityBaselineGate().run(insecure_s3_dir)
    assert result.verdict in (Verdict.FAIL, Verdict.WARN)
