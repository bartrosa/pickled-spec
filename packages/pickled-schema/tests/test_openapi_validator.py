from __future__ import annotations

from pathlib import Path

import pytest

openapi_spec_validator = pytest.importorskip("openapi_spec_validator")

from pickled_schema.openapi.parser import load_openapi_file  # noqa: E402
from pickled_schema.openapi.validator import validate_openapi_dict  # noqa: E402


def test_users_crud_validates(openapi_fixture: Path) -> None:
    spec_dict, _, _ = load_openapi_file(openapi_fixture)
    validate_openapi_dict(spec_dict)
