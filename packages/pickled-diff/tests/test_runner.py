from __future__ import annotations

import sys

from pickled_diff.runner import CallableRunner, OracleRunner, SubprocessRunner


def test_callable_runner_returns_output_on_success() -> None:
    runner = CallableRunner(lambda s: s.upper(), name="t")
    out = runner.run("hello")
    assert out.stdout == "HELLO"
    assert out.exit_code == 0
    assert out.error == ""


def test_callable_runner_catches_exception_and_sets_error() -> None:
    def boom(_: str) -> str:
        raise ValueError("nope")

    runner = CallableRunner(boom)
    out = runner.run("x")
    assert out.stdout == ""
    assert out.exit_code == 1
    assert "nope" in out.error


def test_subprocess_runner_captures_stdout() -> None:
    cmd = [sys.executable, "-c", "import sys; print(int(sys.stdin.read()) * 2)"]
    runner = SubprocessRunner(cmd, timeout_seconds=10.0)
    out = runner.run("3")
    assert out.error == ""
    assert out.stdout.strip() == "6"


def test_subprocess_runner_timeout_sets_error_field() -> None:
    cmd = [sys.executable, "-c", "import time; time.sleep(5)"]
    runner = SubprocessRunner(cmd, timeout_seconds=0.01)
    out = runner.run("")
    assert out.error
    assert "timeout" in out.error.lower()


def test_subprocess_runner_missing_command_sets_error_field() -> None:
    runner = SubprocessRunner(["/no/such/binary/pickled-diff-test"], timeout_seconds=5.0)
    out = runner.run("1")
    assert out.error != ""


def test_callable_runner_is_oracle_runner_protocol() -> None:
    runner = CallableRunner(lambda s: s)
    assert isinstance(runner, OracleRunner)
