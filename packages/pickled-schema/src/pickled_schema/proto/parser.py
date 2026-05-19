"""Parse .proto files by invoking grpc_tools.protoc."""

from __future__ import annotations

import base64
import subprocess
import sys
import tempfile
from pathlib import Path

from pickled_schema.types import SchemaArtifact, SchemaFormat


def parse_proto_file(
    proto_path: Path,
    proto_dir: Path | None = None,
) -> SchemaArtifact:
    """Parse a .proto file and return a descriptor set as base64 text."""
    pd = proto_dir or proto_path.parent
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "descriptor.bin"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "grpc_tools.protoc",
                f"--proto_path={pd}",
                f"--descriptor_set_out={out}",
                "--include_imports",
                str(proto_path),
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            err = (result.stderr or result.stdout or "protoc failed").strip()
            msg = f"protoc failed: {err}"
            raise RuntimeError(msg)
        data = out.read_bytes()
    return SchemaArtifact(
        format=SchemaFormat.proto3,
        content=base64.b64encode(data).decode("ascii"),
        endpoint_id=None,
        source="file",
    )


__all__ = ["parse_proto_file"]
