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


def test_cli_counts_citations_under_rule_block(tmp_path: Path) -> None:
    """Rule-block scenarios must contribute their citation tags.

    Regression test: a previous version of the pytest-bdd adapter
    silently dropped scenarios nested under ``Rule:`` blocks, which
    caused the coverage gate to falsely report missing citations and
    fail compliance even when the feature did cover the rule.
    """
    feature_text = (
        "Feature: T\n"
        "  Rule: Coverage of 1.1\n"
        "    @tiny_corpus:1.1\n"
        "    Scenario: S\n"
        "      Given x\n"
    )
    feat = tmp_path / "rule_in_feature.feature"
    feat.write_text(feature_text, encoding="utf-8")

    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--corpus-path", str(TINY_CORPUS), "--feature", str(feat)],
    )
    assert r.exit_code == 0, r.stdout + r.stderr
