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


def test_cli_feature_level_citation_tags_are_honoured(tmp_path: Path) -> None:
    """Feature-level @hipaa tags must count as citations on every scenario.

    Without feature-tag inheritance, a feature that hoists a regulatory
    citation to the feature header silently fails the coverage gate even
    though every scenario in the file *should* count as a citation — a
    false-negative compliance verdict.
    """
    feat = tmp_path / "feature_tag.feature"
    feat.write_text(
        "@hipaa:(b)\n"
        "Feature: Audit logging\n"
        "\n"
        "  Scenario: Each access is recorded\n"
        "    Given a clinician opens a patient record\n"
        "    Then the audit log records the access\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["check", "--corpus", "hipaa-164.312", "--feature", str(feat)],
    )
    out = result.stdout + result.stderr
    # Other required rules are still uncited so the overall verdict is
    # FAIL, but `(b)` must appear in the coverage table as covered (✅)
    # and must NOT show up under "Required gaps".
    required_section = out.split("## Required gaps")
    assert len(required_section) > 1, "expected required-gaps section"
    gaps = required_section[1].split("## Addressable gaps")[0]
    assert "### `(b)`" not in gaps, "feature-level @hipaa:(b) was not honoured"
    # And the coverage table row for (b) carries the covered marker.
    table = out.split("## Coverage")[1].split("## ")[0]
    table_lines = [ln for ln in table.splitlines() if "`(b)`" in ln]
    assert table_lines, "expected a coverage row for (b)"
    assert "✅" in table_lines[0], (
        f"(b) should be marked covered via feature-level tag; row was: {table_lines[0]!r}"
    )


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
