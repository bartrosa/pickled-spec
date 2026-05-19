"""Structural validation for OpenAPI 3.x documents."""

from __future__ import annotations

from typing import Any

from pickled_schema.types import SchemaValidationError


def validate_openapi_dict(spec_dict: dict[str, Any]) -> None:
    """Validate *spec_dict* with openapi-spec-validator."""
    try:
        from openapi_spec_validator import validate
        from openapi_spec_validator.exceptions import OpenAPIError
        from openapi_spec_validator.validation.exceptions import (
            OpenAPIValidationError,
        )
    except ImportError as exc:
        msg = "install pickled-schema[openapi] for OpenAPI validation"
        raise SchemaValidationError(msg) from exc

    try:
        validate(spec_dict)
    except (OpenAPIError, OpenAPIValidationError) as exc:
        errors = [str(exc)]
        nested = getattr(exc, "schema_errors", None)
        if nested:
            errors.extend(str(e) for e in nested)
        raise SchemaValidationError("OpenAPI validation failed", errors=errors) from exc


def validate_openapi_text(text: str, *, suffix: str = ".yaml") -> None:
    from pickled_schema.openapi.parser import parse_openapi_text

    spec_dict, _ = parse_openapi_text(text, suffix=suffix)
    validate_openapi_dict(spec_dict)


__all__ = ["validate_openapi_dict", "validate_openapi_text"]
