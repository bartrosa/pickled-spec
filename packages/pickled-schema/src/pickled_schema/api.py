"""Cross-package contracts for schema discovery."""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from pickled_schema.types import SchemaArtifact


@runtime_checkable
class SchemaRegistry(Protocol):
    """Lookup schemas referenced from Gherkin or other artifacts.

    ``pickled-data`` (Week 5) will depend on this protocol to resolve
  ``@schema:endpoint:*`` tags to concrete schema documents.
    """

    def find_schema_by_tag(self, tag: str) -> SchemaArtifact | None:
        """Return a schema for ``tag``, or ``None`` if unknown."""
        ...


__all__ = ["SchemaRegistry"]
