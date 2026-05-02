"""Prompt templates for pickled-bdd.

Templates live as `.md` files alongside this module so that prompt edits
do not require code changes. Loaded via `pickled_core.PromptTemplate`.
"""

from pathlib import Path


def template_path(name: str) -> Path:
    """Return the filesystem path to a prompt template."""
    return Path(__file__).resolve().parent / name
