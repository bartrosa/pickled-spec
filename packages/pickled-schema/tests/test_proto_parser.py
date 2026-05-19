from __future__ import annotations

from pathlib import Path

import pytest

grpc_tools = pytest.importorskip("grpc_tools")

from pickled_schema.proto.parser import parse_proto_file  # noqa: E402
from pickled_schema.types import SchemaFormat  # noqa: E402


def test_parse_proto_descriptor(proto_fixture: Path) -> None:
    artifact = parse_proto_file(proto_fixture)
    assert artifact.format is SchemaFormat.proto3
    assert artifact.source == "file"
    assert len(artifact.content) > 20
