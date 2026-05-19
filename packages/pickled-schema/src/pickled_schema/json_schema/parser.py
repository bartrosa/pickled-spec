"""Load JSON Schema documents."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from pickled_schema.types import SchemaArtifact, SchemaFormat, SchemaParseError

# v0.2: JSON Schema drafter (LLM-driven) is not implemented yet.


def load_json_schema_file(path: Path) -> tuple[dict[str, Any], SchemaArtifact]:
    raw = path.read_text(encoding="utf-8")
    data = json.loads(raw)
    if not isinstance(data, dict):
        msg = "JSON Schema root must be an object"
        raise SchemaParseError(msg)
    artifact = SchemaArtifact(
        format=SchemaFormat.json_schema_2020_12,
        content=raw,
        endpoint_id=None,
        source="file",
    )
    return data, artifact


__all__ = ["load_json_schema_file"]
