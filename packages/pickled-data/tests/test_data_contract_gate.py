from __future__ import annotations

from pickled_core import Verdict
from pickled_data.gates import DataContractGate
from pickled_schema.types import SchemaArtifact, SchemaFormat


class FakeRegistry:
    def __init__(self, artifact: SchemaArtifact | None) -> None:
        self._artifact = artifact

    def find_schema_by_tag(self, tag: str) -> SchemaArtifact | None:
        _ = tag
        return self._artifact


_OPENAPI = """
openapi: 3.1.0
info: {title: t, version: "1"}
paths:
  /users/{id}:
    get:
      responses:
        "200":
          description: ok
          content:
            application/json:
              schema:
                type: object
                properties:
                  id: {type: string}
                  email: {type: string}
                  name: {type: string}
"""


def test_contract_pass() -> None:
    artifact = SchemaArtifact(
        format=SchemaFormat.openapi_3_1,
        content=_OPENAPI,
        endpoint_id="GET-/users/{id}",
        source="file",
    )
    gate = DataContractGate(FakeRegistry(artifact))
    sql = "SELECT id, email, name FROM users WHERE id = 1"
    result = gate.run(
        sql,
        context={"endpoint_tag": "@schema:endpoint:GET-/users/{id}"},
    )
    assert result.verdict is Verdict.PASS


def test_contract_fail_column_mismatch() -> None:
    artifact = SchemaArtifact(
        format=SchemaFormat.openapi_3_1,
        content=_OPENAPI,
        endpoint_id=None,
        source="file",
    )
    gate = DataContractGate(FakeRegistry(artifact))
    sql = "SELECT id, email, phone FROM users"
    result = gate.run(
        sql,
        context={"endpoint_tag": "@schema:endpoint:GET-/users/{id}"},
    )
    assert result.verdict is Verdict.FAIL


def test_contract_warn_no_registry() -> None:
    gate = DataContractGate(None)
    result = gate.run(
        "SELECT 1",
        context={"endpoint_tag": "@schema:endpoint:GET-/x"},
    )
    assert result.verdict is Verdict.WARN
