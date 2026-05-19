from __future__ import annotations

import json
from pathlib import Path

import pytest
from pickled_core.mcp.resources import (
    resource_list_runs,
    resource_run_llm_calls,
    resource_run_manifest,
    validate_run_id,
)


def test_validate_run_id_rejects_traversal() -> None:
    with pytest.raises(ValueError):
        validate_run_id("../etc")


def test_list_runs_empty(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PICKLED_RUNS_DIR", str(tmp_path))
    data = json.loads(resource_list_runs())
    assert data == []


def test_manifest_and_llm_calls(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("PICKLED_RUNS_DIR", str(tmp_path))
    run = tmp_path / "01HZZZZZZZZZZZZZZZZZZZZZZZ"
    run.mkdir()
    (run / "manifest.json").write_text('{"run_id":"01HZZZZZZZZZZZZZZZZZZZZZZZ"}', encoding="utf-8")
    (run / "llm_calls.jsonl").write_text('{"call_id":"a"}\n{"call_id":"b"}\n', encoding="utf-8")
    assert "01HZZZZZZZZZZZZZZZZZZZZZZZ" in resource_list_runs()
    assert "run_id" in resource_run_manifest("01HZZZZZZZZZZZZZZZZZZZZZZZ")
    tail = resource_run_llm_calls("01HZZZZZZZZZZZZZZZZZZZZZZZ", 1)
    assert '"call_id":"b"' in tail
