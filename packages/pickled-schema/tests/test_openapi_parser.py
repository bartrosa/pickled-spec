from __future__ import annotations

from pathlib import Path

import pytest
from pickled_schema.openapi.parser import detect_format, load_openapi_file
from pickled_schema.types import SchemaFormat, SchemaParseError


def test_detect_openapi_31(openapi_fixture: Path) -> None:
    spec_dict, fmt, artifact = load_openapi_file(openapi_fixture)
    assert fmt is SchemaFormat.openapi_3_1
    assert spec_dict["openapi"] == "3.1.0"
    assert artifact.source == "file"
    assert "/users" in artifact.content


def test_reject_swagger_2() -> None:
    with pytest.raises(SchemaParseError, match="2.0"):
        detect_format({"swagger": "2.0", "info": {"title": "x", "version": "1"}})
