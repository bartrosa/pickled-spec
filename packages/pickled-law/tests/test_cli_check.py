from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from pickled_law.cli import main

PKG = Path(__file__).resolve().parent.parent
EXAMPLE = PKG / "examples" / "ehr_authentication.feature"
TINY_CORPUS = PKG / "tests" / "fixtures" / "tiny_corpus.yaml"


def test_cli_example_feature_exit_fail_and_gaps() -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "check",
            "--corpus",
            "hipaa-164.312",
            "--feature",
            str(EXAMPLE),
        ],
    )
    assert result.exit_code == 1
    out = result.stdout + result.stderr
    assert "(c)(1)" in out
    assert "(e)(1)" in out
    assert "(a)(2)(iii)" in out
    req = out.split("## Required gaps")[1].split("## Addressable gaps")[0]
    assert "### `(d)`" not in req


def test_cli_corpus_path_happy(tmp_path: Path) -> None:
    tiny_feat = tmp_path / "tiny_corpus.feature"
    tiny_feat.write_text(
        'Feature: T\n  @tiny_corpus:1.1\n  Scenario: S\n    Given x\n',
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--corpus-path", str(TINY_CORPUS), "--feature", str(tiny_feat)],
    )
    assert r.exit_code == 0


def test_cli_quiet() -> None:
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        [
            "check",
            "--corpus",
            "hipaa-164.312",
            "--feature",
            str(EXAMPLE),
            "--quiet",
        ],
    )
    assert r.exit_code == 1
    assert r.stdout.strip().startswith("FAIL:")
    assert "# Requirements" not in r.stdout


def test_cli_both_corpus_flags_errors() -> None:
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        [
            "check",
            "--corpus",
            "hipaa",
            "--corpus-path",
            str(TINY_CORPUS),
            "--feature",
            str(EXAMPLE),
        ],
    )
    assert r.exit_code != 0
    assert "exactly one" in (r.stdout + r.stderr).lower()


def _bundled_hipaa_path() -> Path:
    """Locate the bundled HIPAA corpus YAML in either dev or wheel layout."""
    pkg_root = Path(__file__).resolve().parent.parent
    candidates = (
        pkg_root / "src" / "pickled_law" / "corpora" / "hipaa" / "164_312.yaml",
        pkg_root / "corpora" / "hipaa" / "164_312.yaml",
    )
    for c in candidates:
        if c.is_file():
            return c
    raise AssertionError(f"Bundled HIPAA corpus not found in {candidates}")


def test_cli_corpus_path_uses_declared_short_name() -> None:
    """Loading the bundled HIPAA corpus via ``--corpus-path`` must agree with ``--corpus``.

    Regression: the CLI used to derive the citation-tag prefix from the
    YAML filename stem when a corpus was loaded via ``--corpus-path``.
    The bundled HIPAA corpus is shipped as ``164_312.yaml`` while its
    canonical tag prefix is ``hipaa``, so any project loading that file
    by path saw every ``@hipaa:...`` tag silently dropped by the
    coverage gate's corpus filter — and a feature that did cite the
    corpus correctly was reported as missing every required rule.
    """
    bundled = _bundled_hipaa_path()
    runner = CliRunner(mix_stderr=False)
    by_name = runner.invoke(
        main,
        ["check", "--corpus", "hipaa-164.312", "--feature", str(EXAMPLE), "--quiet"],
    )
    by_path = runner.invoke(
        main,
        ["check", "--corpus-path", str(bundled), "--feature", str(EXAMPLE), "--quiet"],
    )
    assert by_name.exit_code == by_path.exit_code, (
        f"named={by_name.stdout!r} {by_name.stderr!r} | "
        f"path={by_path.stdout!r} {by_path.stderr!r}"
    )
    assert by_name.stdout.strip() == by_path.stdout.strip(), (
        "Coverage gate must report the same verdict regardless of "
        "whether the corpus was loaded via --corpus or --corpus-path."
    )


def test_cli_corpus_short_name_override(tmp_path: Path) -> None:
    """``--corpus-short-name`` overrides the derived/declared prefix."""
    feat = tmp_path / "feat.feature"
    feat.write_text(
        "Feature: T\n  @policy:1.1\n  Scenario: S\n    Given x\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        [
            "check",
            "--corpus-path",
            str(TINY_CORPUS),
            "--corpus-short-name",
            "policy",
            "--feature",
            str(feat),
        ],
    )
    assert r.exit_code == 0, r.stdout + r.stderr
