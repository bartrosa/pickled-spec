"""Built-in rule set paths.

Maps short names to YAML files shipped with the package. The CLI uses this
to resolve ``--ruleset team-api-conv`` without users needing to know filesystem
layout.
"""

from __future__ import annotations

from pathlib import Path


def _rulesets_dir() -> Path:
    """Resolve bundled rule sets: wheel layout or dev tree."""
    here = Path(__file__).resolve().parent
    wheel_layout = here / "rulesets"
    if (wheel_layout / "examples" / "team-api-conventions.yaml").is_file():
        return wheel_layout
    repo_layout = here.parent.parent / "rulesets"
    if (repo_layout / "examples" / "team-api-conventions.yaml").is_file():
        return repo_layout
    return wheel_layout


_RULESETS_DIR: Path = _rulesets_dir()

BUILTIN_RULESETS: dict[str, Path] = {
    "team-api-conv": _RULESETS_DIR / "examples" / "team-api-conventions.yaml",
    "review-checklist": _RULESETS_DIR / "examples" / "code-review-checklist.yaml",
}
"""Map of rule set short names to YAML paths."""


def resolve_ruleset_name(name: str) -> Path:
    """Resolve a built-in rule set short name to a path.

    Raises `KeyError` with a helpful message on unknown names.
    """
    if name not in BUILTIN_RULESETS:
        raise KeyError(
            f"Unknown rule set {name!r}. Available: {sorted(BUILTIN_RULESETS.keys())}"
        )
    return BUILTIN_RULESETS[name]
