"""Meta-validation for JSON Schema documents (schema-of-schema)."""

from __future__ import annotations

from typing import Any

from pickled_schema.types import SchemaValidationError


def validate_json_schema_document(schema: dict[str, Any]) -> None:
    """Verify the document is a well-formed Draft 2020-12 schema."""
    try:
        from jsonschema import Draft202012Validator
        from jsonschema.exceptions import SchemaError
    except ImportError as exc:
        msg = "install pickled-schema[json-schema] for JSON Schema validation"
        raise SchemaValidationError(msg) from exc

    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as exc:
        raise SchemaValidationError(
            "JSON Schema meta-validation failed",
            errors=[str(exc)],
        ) from exc


__all__ = ["validate_json_schema_document"]
