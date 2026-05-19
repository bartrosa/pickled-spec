"""Prompt templates for pickled-schema gates."""

from pathlib import Path


def template_path(name: str) -> Path:
    return Path(__file__).resolve().parent / name
