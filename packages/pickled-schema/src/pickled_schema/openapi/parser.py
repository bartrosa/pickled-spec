"""Load OpenAPI 3.x documents from YAML or JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import yaml

from pickled_schema.types import SchemaArtifact, SchemaFormat, SchemaParseError


def detect_format(spec_dict: dict[str, Any]) -> SchemaFormat:
    """Infer OpenAPI version from a parsed document root."""
    if "swagger" in spec_dict:
        msg = "OpenAPI 2.0 (swagger field) is not supported in v0.1"
        raise SchemaParseError(msg)
    version = spec_dict.get("openapi")
    if not isinstance(version, str):
        msg = "missing or invalid top-level 'openapi' version field"
        raise SchemaParseError(msg)
    if version.startswith("3.2"):
        return SchemaFormat.openapi_3_2
    if version.startswith("3.1"):
        return SchemaFormat.openapi_3_1
    if version.startswith("3.0"):
        return SchemaFormat.openapi_3_0
    msg = f"unsupported OpenAPI version {version!r}"
    raise SchemaParseError(msg)


def _load_text(path: Path) -> tuple[dict[str, Any], str]:
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        data = yaml.safe_load(raw)
    elif suffix == ".json":
        data = json.loads(raw)
    else:
        try:
            data = yaml.safe_load(raw)
        except yaml.YAMLError as exc:
            msg = f"cannot parse {path}: not valid YAML or JSON"
            raise SchemaParseError(msg) from exc
    if not isinstance(data, dict):
        msg = "schema root must be a mapping"
        raise SchemaParseError(msg)
    return data, raw


def parse_openapi_text(text: str, *, suffix: str = ".yaml") -> tuple[dict[str, Any], SchemaFormat]:
    """Parse OpenAPI YAML/JSON text."""
    data = json.loads(text) if suffix.lower() == ".json" else yaml.safe_load(text)
    if not isinstance(data, dict):
        msg = "schema root must be a mapping"
        raise SchemaParseError(msg)
    return data, detect_format(data)


def load_openapi_file(path: Path) -> tuple[dict[str, Any], SchemaFormat, SchemaArtifact]:
    """Load a file and return parsed dict, detected format, and artifact."""
    data, raw = _load_text(path)
    fmt = detect_format(data)
    artifact = SchemaArtifact(
        format=fmt,
        content=raw,
        endpoint_id=None,
        source="file",
    )
    return data, fmt, artifact


__all__ = ["detect_format", "load_openapi_file", "parse_openapi_text"]
