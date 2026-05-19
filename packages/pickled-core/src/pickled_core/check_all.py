"""Run every ``pickled.gates`` entry point against a workspace directory."""

from __future__ import annotations

from dataclasses import dataclass
from importlib.metadata import entry_points
from pathlib import Path

from pickled_core import GateResult, Verdict


@dataclass(frozen=True, slots=True)
class CheckAllRow:
    package: str
    gate: str
    verdict: Verdict
    findings: int
    notes: str


def _worst(verdicts: list[Verdict]) -> Verdict:
    if Verdict.FAIL in verdicts:
        return Verdict.FAIL
    if Verdict.WARN in verdicts:
        return Verdict.WARN
    return Verdict.PASS


def run_check_all(workdir: Path, *, warn_ok: bool = False) -> tuple[list[CheckAllRow], int]:
    """Execute all registered gate runners; return rows and process exit code.

    When ``warn_ok`` is true, WARN verdicts do not raise the exit code above 0
    (FAIL still yields exit code 2).
    """
    rows: list[CheckAllRow] = []
    all_verdicts: list[Verdict] = []

    for ep in sorted(entry_points(group="pickled.gates"), key=lambda e: e.name):
        runner = ep.load()
        try:
            results: list[GateResult] = runner(workdir)
        except Exception as exc:
            results = [
                GateResult(
                    gate_name=f"{ep.name}.error",
                    verdict=Verdict.FAIL,
                    notes=str(exc),
                )
            ]
        if not results:
            results = [
                GateResult(
                    gate_name=f"{ep.name}.noop",
                    verdict=Verdict.PASS,
                    notes="no checks run",
                )
            ]
        for gr in results:
            rows.append(
                CheckAllRow(
                    package=ep.name,
                    gate=gr.gate_name,
                    verdict=gr.verdict,
                    findings=len(gr.findings),
                    notes=gr.notes,
                )
            )
            all_verdicts.append(gr.verdict)

    worst = _worst(all_verdicts)
    if worst is Verdict.FAIL:
        return rows, 2
    if worst is Verdict.WARN and not warn_ok:
        return rows, 1
    return rows, 0


def format_table(rows: list[CheckAllRow]) -> str:
    headers = ("package", "gate", "verdict", "findings", "notes")
    col_widths = [len(h) for h in headers]
    lines: list[list[str]] = []
    for row in rows:
        cells = [
            row.package,
            row.gate,
            row.verdict.value,
            str(row.findings),
            row.notes[:60] + ("…" if len(row.notes) > 60 else ""),
        ]
        lines.append(cells)
        for i, cell in enumerate(cells):
            col_widths[i] = max(col_widths[i], len(cell))

    def fmt_row(cells: list[str]) -> str:
        return "  ".join(cell.ljust(col_widths[i]) for i, cell in enumerate(cells))

    out = [fmt_row(list(headers)), fmt_row(["-" * w for w in col_widths])]
    out.extend(fmt_row(line) for line in lines)
    return "\n".join(out)


__all__ = ["CheckAllRow", "format_table", "run_check_all"]
