"""Annotations using typing.Literal must not crash the resolver."""

from __future__ import annotations

from typing import Literal


def entry(mode: Literal["terraform", "opentofu"]) -> str:
    return mode
