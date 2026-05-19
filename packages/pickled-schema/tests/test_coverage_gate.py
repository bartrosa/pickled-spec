from __future__ import annotations

from pathlib import Path

import yaml
from pickled_core import Verdict
from pickled_schema.gates import SchemaCoverageGate


def _minimal_spec() -> dict:
    return {
        "openapi": "3.1.0",
        "info": {"title": "t", "version": "1"},
        "paths": {
            "/users": {
                "get": {"responses": {"200": {"description": "ok"}}},
            },
        },
    }


def test_coverage_pass_when_tag_matches(tmp_path: Path) -> None:
    feature = tmp_path / "api.feature"
    feature.write_text(
        "@schema:endpoint:GET-/users\n"
        "Scenario: List\n"
        "  Given the API\n",
        encoding="utf-8",
    )
    result = SchemaCoverageGate().run(
        _minimal_spec(),
        context={"feature_paths": [feature]},
    )
    assert result.verdict is Verdict.PASS


def test_coverage_fail_when_tag_missing(tmp_path: Path) -> None:
    feature = tmp_path / "api.feature"
    feature.write_text(
        "@schema:endpoint:POST-/orders\n"
        "Scenario: Create order\n",
        encoding="utf-8",
    )
    result = SchemaCoverageGate().run(
        _minimal_spec(),
        context={"feature_paths": [feature]},
    )
    assert result.verdict is Verdict.FAIL
    assert len(result.findings) == 1


def test_coverage_with_feature_texts() -> None:
    text = "@schema:endpoint:GET-/users\nScenario: x\n"
    result = SchemaCoverageGate().run(
        _minimal_spec(),
        context={"feature_texts": [text]},
    )
    assert result.verdict is Verdict.PASS


def test_coverage_against_users_fixture(openapi_fixture: Path, tmp_path: Path) -> None:
    spec_dict = yaml.safe_load(openapi_fixture.read_text(encoding="utf-8"))
    feature = tmp_path / "users.feature"
    feature.write_text(
        "@schema:endpoint:GET-/users\n"
        "@schema:endpoint:POST-/users\n"
        "@schema:endpoint:GET-/users/{id}\n"
        "Scenario: CRUD\n",
        encoding="utf-8",
    )
    result = SchemaCoverageGate().run(
        spec_dict,
        context={"feature_paths": [feature]},
    )
    assert result.verdict is Verdict.PASS
