from __future__ import annotations

from pickled_core.cost import load_default_catalogue


def test_load_bundled_yaml() -> None:
    c = load_default_catalogue()
    row = c.row_for("openai", "gpt-4o")
    assert row is not None
    assert row.input_per_mtok > 0


def test_sha256_stable_across_reads() -> None:
    a = load_default_catalogue()
    b = load_default_catalogue()
    assert a.content_sha256 == b.content_sha256
    assert len(a.content_sha256) == 64
