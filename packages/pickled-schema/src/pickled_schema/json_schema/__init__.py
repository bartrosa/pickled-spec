"""JSON Schema Draft 2020-12 parsing and meta-validation."""

from pickled_schema.json_schema.parser import load_json_schema_file
from pickled_schema.json_schema.validator import validate_json_schema_document

__all__ = ["load_json_schema_file", "validate_json_schema_document"]
