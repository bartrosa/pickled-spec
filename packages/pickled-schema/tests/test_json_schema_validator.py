from __future__ import annotations

from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from pickled_schema.json_schema.parser import load_json_schema_file  # noqa: E402
from pickled_schema.json_schema.validator import validate_json_schema_document  # noqa: E402


def test_user_schema_meta_validates(json_schema_fixture: Path) -> None:
    schema_dict, _ = load_json_schema_file(json_schema_fixture)
    validate_json_schema_document(schema_dict)
