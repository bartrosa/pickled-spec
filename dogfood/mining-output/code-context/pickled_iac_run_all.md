# Code context: run_all

- **Surface id:** pickled_iac_run_all
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 6 | **Total lines:** 184 | **Truncated:** False

## Root: pickled_iac.gates_runner.run_all

```python
def run_all(workdir: Path | str) -> list[GateResult]:
    """``terraform validate`` and optional Trivy scan on ``infra/``."""
    root = Path(workdir).resolve()
    infra = root / "infra"
    if not infra.is_dir():
        return [
            GateResult(
                gate_name="iac.infra",
                verdict=Verdict.WARN,
                notes="no infra/ directory",
            )
        ]

    results: list[GateResult] = []
    try:
        vr = validate(infra)
    except IaCToolMissingError as exc:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.WARN,
                notes=str(exc),
            )
        )
    except Exception as exc:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.FAIL,
                notes=str(exc),
            )
        )
    else:
        results.append(
            GateResult(
                gate_name="iac.validate",
                verdict=Verdict.PASS if vr.valid else Verdict.FAIL,
                notes="; ".join(vr.diagnostics) or "ok",
            )
        )

    sec = SecurityBaselineGate().run(infra)
    results.append(
        GateResult(
            gate_name=sec.gate_name,
            verdict=sec.verdict,
            findings=sec.findings,
            notes=sec.notes,
        )
    )
    return results
```

## Callee: pickled_iac.oracle.validate (hop 1)

```python
def validate(tf_dir: Path) -> ValidateResult:
    """Run ``terraform validate -json`` (or OpenTofu equivalent)."""
    binary = iac_binary()
    _init_if_needed(tf_dir, binary)
    proc = _run([binary, "validate", "-json"], cwd=tf_dir)
    fmt: Literal["terraform", "opentofu"] = "opentofu" if binary == "opentofu" else "terraform"
    if proc.returncode != 0 and not proc.stdout.strip():
        err = (proc.stderr or "validate failed").strip()
        return ValidateResult(valid=False, diagnostics=[err], format=fmt)
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError:
        err = (proc.stderr or proc.stdout or "invalid validate JSON").strip()
        return ValidateResult(valid=False, diagnostics=[err], format=fmt)
    valid = bool(payload.get("valid"))
    diags: list[str] = []
    for d in payload.get("diagnostics", []):
        if isinstance(d, dict):
            summary = d.get("summary") or d.get("detail") or str(d)
            diags.append(str(summary))
    return ValidateResult(valid=valid, diagnostics=diags, format=fmt)
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

## Callee: pickled_iac.oracle.iac_binary (hop 2)

```python
def iac_binary() -> Literal["terraform", "opentofu"]:
    """Return the detected IaC CLI binary name."""
    if _IAC_BIN is None:
        raise IaCToolMissingError(
            "neither 'terraform' nor 'tofu' found on PATH; "
            "install Terraform >=1.7.5 or OpenTofu >=1.8"
        )
    return _IAC_BIN
```

## Callee: pickled_iac.oracle._init_if_needed (hop 2)

```python
def _init_if_needed(tf_dir: Path, binary: Literal["terraform", "opentofu"]) -> None:
    if (tf_dir / ".terraform").exists():
        return
    init = _run([binary, "init", "-input=false", "-backend=false"], cwd=tf_dir)
    if init.returncode != 0:
        err = (init.stderr or init.stdout or "terraform init failed").strip()
        msg = f"{binary} init failed: {err}"
        raise RuntimeError(msg)
```

## Callee: pickled_iac.oracle._run (hop 2)

```python
def _run(cmd: list[str], *, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        cmd,
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        env={**os.environ, "TF_IN_AUTOMATION": "1"},
    )
```
