from __future__ import annotations

import json
import sys
from pathlib import Path

from click.testing import CliRunner
from pickled_diff.cli import main

_EXAMPLES = Path(__file__).resolve().parents[1] / "examples"


def test_cli_help_lists_verify_and_serve() -> None:
    runner = CliRunner()
    result = runner.invoke(main, ["--help"])
    assert result.exit_code == 0
    assert "verify" in result.output
    assert "serve" in result.output


def test_cli_verify_pass_exits_zero(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps([{"name": "one", "payload": "4"}]),
        encoding="utf-8",
    )
    oracle = f"{sys.executable} {_EXAMPLES / 'trivial_oracle.py'}"
    candidate = f"{sys.executable} {_EXAMPLES / 'trivial_candidate.py'}"
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "verify",
            "--oracle",
            oracle,
            "--candidate",
            candidate,
            "--corpus",
            str(corpus),
        ],
    )
    assert result.exit_code == 0, result.output
    payload = json.loads(result.output)
    assert payload["verdict"] == "pass"


def test_cli_verify_fail_exits_two(tmp_path: Path) -> None:
    corpus = tmp_path / "corpus.json"
    corpus.write_text(
        json.dumps([{"name": "one", "payload": "2"}]),
        encoding="utf-8",
    )
    oracle = f"{sys.executable} {_EXAMPLES / 'trivial_oracle.py'}"
    bad = (
        f'{sys.executable} -c "import sys; print(int(sys.stdin.read()) * 99)"'
    )
    runner = CliRunner()
    result = runner.invoke(
        main,
        [
            "verify",
            "--oracle",
            oracle,
            "--candidate",
            bad,
            "--corpus",
            str(corpus),
        ],
    )
    assert result.exit_code == 2, result.output
