from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture
def openapi_fixture() -> Path:
    return FIXTURES / "openapi" / "users-crud.yaml"


@pytest.fixture
def json_schema_fixture() -> Path:
    return FIXTURES / "json_schema" / "user.json"


@pytest.fixture
def proto_fixture() -> Path:
    return FIXTURES / "proto" / "user.proto"
