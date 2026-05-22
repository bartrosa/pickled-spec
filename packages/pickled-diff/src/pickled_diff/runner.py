"""OracleRunner protocol and default implementations."""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path
from typing import Protocol, runtime_checkable

from pickled_diff.types import OracleOutput


@runtime_checkable
class OracleRunner(Protocol):
    """Runs one implementation against one input and captures output.

    The same protocol is used for both the oracle (reference implementation)
    and the candidate (implementation under verification). The gate composes
    two runners and compares their outputs via a Comparator.
    """

    name: str

    def run(self, input_payload: str) -> OracleOutput: ...


class CallableRunner:
    """In-process runner wrapping a ``Callable[[str], str]``."""

    def __init__(self, fn: Callable[[str], str], *, name: str = "callable") -> None:
        self.name = name
        self._fn = fn

    def run(self, input_payload: str) -> OracleOutput:
        try:
            return OracleOutput(stdout=self._fn(input_payload), exit_code=0)
        except Exception as exc:
            return OracleOutput(stdout="", exit_code=1, error=str(exc))


class SubprocessRunner:
    """Runs a subprocess command, passing ``input_payload`` on stdin (UTF-8)."""

    def __init__(
        self,
        command: list[str],
        *,
        name: str = "subprocess",
        timeout_seconds: float = 30.0,
        cwd: str | Path | None = None,
    ) -> None:
        self.name = name
        self._command = command
        self._timeout = timeout_seconds
        self._cwd = str(cwd) if cwd is not None else None

    def run(self, input_payload: str) -> OracleOutput:
        try:
            completed = subprocess.run(
                self._command,
                input=input_payload,
                capture_output=True,
                text=True,
                timeout=self._timeout,
                check=False,
                cwd=self._cwd,
            )
        except subprocess.TimeoutExpired:
            return OracleOutput(
                stdout="",
                exit_code=-1,
                error=f"timeout after {self._timeout}s",
            )
        except FileNotFoundError as exc:
            return OracleOutput(stdout="", exit_code=-1, error=str(exc))
        except OSError as exc:
            return OracleOutput(stdout="", exit_code=-1, error=str(exc))
        return OracleOutput(
            stdout=completed.stdout,
            exit_code=completed.returncode,
            stderr=completed.stderr,
        )


__all__ = ["CallableRunner", "OracleRunner", "SubprocessRunner"]
