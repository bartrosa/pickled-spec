"""Built-in corpus paths.

Maps short names to the path of corpus YAML files shipped with the
package. The CLI uses this to resolve `--corpus hipaa` to a path
without users needing to know filesystem layout.
"""

from __future__ import annotations

from pathlib import Path


def _corpora_dir() -> Path:
    """Resolve bundled corpora: wheel (`pickled_law/corpora/`) or dev tree."""
    here = Path(__file__).resolve().parent
    wheel_layout = here / "corpora"
    if (wheel_layout / "hipaa" / "164_312.yaml").is_file():
        return wheel_layout
    repo_layout = here.parent.parent / "corpora"
    if (repo_layout / "hipaa" / "164_312.yaml").is_file():
        return repo_layout
    return wheel_layout


_CORPORA_DIR: Path = _corpora_dir()

BUILTIN_CORPORA: dict[str, Path] = {
    "hipaa": _CORPORA_DIR / "hipaa" / "164_312.yaml",
    "hipaa-164.312": _CORPORA_DIR / "hipaa" / "164_312.yaml",
}
"""Map of corpus short names to corpus YAML paths.

`hipaa` is an alias for `hipaa-164.312` for now (single corpus shipped).
When more HIPAA sections land (Privacy Rule, Breach Notification),
`hipaa` becomes ambiguous and will be removed; users will need the
fully-qualified name.
"""


def resolve_corpus_name(name: str) -> Path:
    """Resolve a corpus short name to a path.

    Raises `KeyError` with helpful message on unknown names.
    """
    if name not in BUILTIN_CORPORA:
        raise KeyError(f"Unknown corpus {name!r}. Available: {sorted(BUILTIN_CORPORA.keys())}")
    return BUILTIN_CORPORA[name]
