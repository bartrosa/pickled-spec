"""Schema domain types for pickled-schema."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from typing import Literal


class SchemaFormat(StrEnum):
    """Supported schema artifact formats."""

    openapi_3_0 = "openapi_3_0"
    openapi_3_1 = "openapi_3_1"
    openapi_3_2 = "openapi_3_2"
    json_schema_2020_12 = "json_schema_2020_12"
    proto3 = "proto3"


@dataclass(frozen=True, slots=True)
class SchemaArtifact:
    """A schema document held in memory."""

    format: SchemaFormat
    content: str
    endpoint_id: str | None
    source: Literal["draft", "file"]


class SchemaParseError(ValueError):
    """Raised when a schema file cannot be parsed or its format detected."""


class SchemaValidationError(ValueError):
    """Raised when a schema fails structural validation."""

    def __init__(self, message: str, *, errors: list[str] | None = None) -> None:
        super().__init__(message)
        self.errors: list[str] = list(errors or [])


__all__ = [
    "SchemaArtifact",
    "SchemaFormat",
    "SchemaParseError",
    "SchemaValidationError",
]
