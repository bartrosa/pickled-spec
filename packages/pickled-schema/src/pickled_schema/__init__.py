"""pickled-schema: multi-format schema drafting and verification."""

from pickled_schema.api import SchemaRegistry
from pickled_schema.gates import SchemaAmbiguityGate, SchemaCoverageGate
from pickled_schema.openapi import OpenAPIDrafter
from pickled_schema.types import (
    SchemaArtifact,
    SchemaFormat,
    SchemaParseError,
    SchemaValidationError,
)

__version__ = "0.1.0.dev0"

__all__ = [
    "OpenAPIDrafter",
    "SchemaAmbiguityGate",
    "SchemaArtifact",
    "SchemaCoverageGate",
    "SchemaFormat",
    "SchemaParseError",
    "SchemaRegistry",
    "SchemaValidationError",
    "__version__",
]
