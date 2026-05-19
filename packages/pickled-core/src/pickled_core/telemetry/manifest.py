"""ADR-0004 manifest whitelist enforcement."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

MANIFEST_WHITELIST: frozenset[str] = frozenset(
    {
        "run_id",
        "config_sha256",
        "pricing_sha256",
        "git_sha",
        "hostname_truncated_8",
        "python_version",
        "created_at_utc",
    }
)


class ManifestValidationError(ValueError):
    """Manifest contains disallowed keys or values."""


def validate_manifest(manifest: Mapping[str, Any]) -> None:
    """Ensure *manifest* keys and string values satisfy ADR-0004."""
    extra = set(manifest.keys()) - MANIFEST_WHITELIST
    if extra:
        raise ManifestValidationError(f"manifest keys not on whitelist: {sorted(extra)}")
    for key, value in manifest.items():
        if not isinstance(value, str):
            raise ManifestValidationError(f"manifest[{key!r}] must be a string")
        if "@" in value:
            raise ManifestValidationError(f"manifest[{key!r}] must not contain '@'")
        if value.startswith("/"):
            raise ManifestValidationError(f"manifest[{key!r}] must not be an absolute path")
        if len(value) > 64:
            raise ManifestValidationError(f"manifest[{key!r}] exceeds 64 characters")


def write_manifest(path: Any, manifest: Mapping[str, Any]) -> None:
    """Validate and write manifest JSON."""
    import json
    from pathlib import Path

    validate_manifest(manifest)
    p = Path(path)
    p.write_text(json.dumps(dict(manifest), indent=2, sort_keys=True) + "\n", encoding="utf-8")


__all__ = [
    "MANIFEST_WHITELIST",
    "ManifestValidationError",
    "validate_manifest",
    "write_manifest",
]
