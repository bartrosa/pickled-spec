from __future__ import annotations

from pathlib import Path

from click.testing import CliRunner
from pickled_rules.cli import main

PKG = Path(__file__).resolve().parent.parent
TINY = PKG / "tests" / "fixtures" / "tiny_ruleset.yaml"
PARTIAL = PKG / "tests" / "fixtures" / "partial_coverage.feature"


def test_cli_builtin_partial_coverage_fails_with_strict_gaps() -> None:
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        [
            "check",
            "--ruleset",
            "team-api-conv",
            "--feature",
            str(PARTIAL),
        ],
    )
    assert result.exit_code == 1
    out = result.stdout + result.stderr
    assert "naming.2" in out
    assert "timestamps.1" in out
    strict = out.split("## Unreferenced strict rules")[1].split("## Unreferenced advisory")[0]
    assert "naming.1" not in strict or "### `naming.1`" not in strict


def test_cli_ruleset_path_happy(tmp_path: Path) -> None:
    feat = tmp_path / "tiny_ruleset.feature"
    feat.write_text(
        'Feature: T\n  @tiny_ruleset:1.1\n  Scenario: S\n    Given x\n',
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", str(TINY), "--feature", str(feat)],
    )
    assert r.exit_code == 0


def test_cli_quiet() -> None:
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", "team-api-conv", "--feature", str(PARTIAL), "--quiet"],
    )
    assert r.exit_code == 1
    assert r.stdout.strip().startswith("FAIL:")
    assert "# Coverage report" not in r.stdout


def test_cli_feature_level_tags(tmp_path: Path) -> None:
    feat = tmp_path / "feature_tag.feature"
    feat.write_text(
        "@team-api-conv:errors.1\n"
        "Feature: Error handling\n"
        "\n"
        "  Scenario: Problem details returned\n"
        "    Given an invalid request\n"
        "    Then the response is problem+json\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    result = runner.invoke(
        main,
        ["check", "--ruleset", "team-api-conv", "--feature", str(feat)],
    )
    out = result.stdout + result.stderr
    strict = out.split("## Unreferenced strict rules")
    assert len(strict) > 1
    gaps = strict[1].split("## Unreferenced advisory")[0]
    assert "### `errors.1`" not in gaps
    table = out.split("## Referenced rules")[1].split("## ")[0]
    assert "`errors.1`" in table and "✅" in table


def test_cli_rule_block_scenario(tmp_path: Path) -> None:
    feat = tmp_path / "rule.feature"
    feat.write_text(
        "Feature: T\n"
        "  Rule: Covers 1.1\n"
        "    @tiny_ruleset:1.1\n"
        "    Scenario: S\n"
        "      Given x\n",
        encoding="utf-8",
    )
    runner = CliRunner(mix_stderr=False)
    r = runner.invoke(
        main,
        ["check", "--ruleset", str(TINY), "--feature", str(feat)],
    )
    assert r.exit_code == 0, r.stdout + r.stderr
