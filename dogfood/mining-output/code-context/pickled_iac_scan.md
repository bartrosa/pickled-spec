# Code context: scan

- **Surface id:** pickled_iac_scan
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 2 | **Total lines:** 102 | **Truncated:** False

## Root: pickled_iac.cli.scan

```python
def scan(tf_dir: Path) -> None:
    """Run Trivy config scan (optional; skips if trivy missing)."""
    result = SecurityBaselineGate().run(tf_dir)
    click.echo(
        json.dumps(
            {
                "verdict": result.verdict.value,
                "notes": result.notes,
                "findings": list(result.findings),
            },
            indent=2,
        )
    )
    if result.verdict is Verdict.FAIL:
        raise SystemExit(2)
```

## Callee: pickled_iac.SecurityBaselineGate.run (hop 1)

```python
def run(
        self,
        target: object,
        *,
        context: dict[str, Any] | None = None,
    ) -> GateResult:
        _ = context
        if not isinstance(target, Path):
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                notes=f"Expected Path to tf dir, got {type(target).__name__}",
            )
        trivy = shutil.which("trivy")
        if trivy is None:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.PASS,
                notes="trivy not found on PATH — security scan skipped",
            )

        proc = subprocess.run(
            [
                trivy,
                "config",
                str(target),
                "--format",
                "json",
                "--severity",
                "HIGH,CRITICAL",
                "--quiet",
            ],
            capture_output=True,
            text=True,
            check=False,
        )
        if proc.returncode not in (0, 1) and not proc.stdout.strip():
            err = (proc.stderr or "trivy failed").strip()
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes=f"trivy error: {err}",
            )

        try:
            report = json.loads(proc.stdout or "{}")
        except json.JSONDecodeError:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                notes="trivy returned non-JSON output",
            )

        critical: list[str] = []
        high: list[str] = []
        for result in report.get("Results", []) or []:
            if not isinstance(result, dict):
                continue
            for mis in result.get("Misconfigurations", []) or []:
                if not isinstance(mis, dict):
                    continue
                sev = str(mis.get("Severity", "")).upper()
                title = str(mis.get("Title", mis.get("ID", "finding")))
                if sev == "CRITICAL":
                    critical.append(title)
                elif sev == "HIGH":
                    high.append(title)

        if critical:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.FAIL,
                findings=tuple(critical),
                notes=f"{len(critical)} CRITICAL finding(s)",
            )
        if high:
            return GateResult(
                gate_name=self.name,
                verdict=Verdict.WARN,
                findings=tuple(high),
                notes=f"{len(high)} HIGH finding(s)",
            )
        return GateResult(
            gate_name=self.name,
            verdict=Verdict.PASS,
            notes="No HIGH or CRITICAL findings.",
        )
```
