# Code context: draft

- **Surface id:** pickled_iac_draft
- **Depth:** callgraph | **Scope:** same-package | **Hops:** 2
- **Units collected:** 5 | **Total lines:** 99 | **Truncated:** False

## Root: pickled_iac.cli.draft

```python
def draft(user_story: str, provider: str, output: Path | None) -> None:
    """Draft a Terraform module from a user story."""
    artifact = IaCDrafter(_build_llm_client()).draft_module(user_story, provider=provider)
    if output:
        output.mkdir(parents=True, exist_ok=True)
        (output / "main.tf").write_text(artifact.content, encoding="utf-8")
        click.echo(f"Wrote {output / 'main.tf'}", err=True)
    else:
        click.echo(artifact.content)
```

## Callee: pickled_iac.IaCDrafter.draft_module (hop 1)

```python
def draft_module(
        self,
        user_story: str,
        provider: str = "aws",
    ) -> IaCArtifact:
        """Draft, validate in a temp dir, and return an IaCArtifact."""
        binary = iac_binary()
        fmt: str = "opentofu" if binary == "opentofu" else "terraform"
        last_error = ""

        for _attempt in range(3):
            feedback = (
                f"\n\nPrevious validation errors:\n{last_error}" if last_error else ""
            )
            prompt = self._template.render(
                provider=provider,
                user_story=user_story,
                error_feedback=feedback,
            )
            from pickled_core.llm.turns import complete_prompt

            hcl = complete_prompt(
                self._llm,
                prompt,
                system="Output only Terraform HCL. No fences, no commentary.",
            ).strip()
            if hcl.startswith("```"):
                lines = hcl.splitlines()
                hcl = "\n".join(
                    line for line in lines if not line.strip().startswith("```")
                ).strip()

            with tempfile.TemporaryDirectory() as tmp:
                root = Path(tmp)
                (root / "main.tf").write_text(hcl, encoding="utf-8")
                result = validate(root)
            if result.valid:
                return IaCArtifact(content=hcl, format=fmt, path=None)  # type: ignore[arg-type]
            last_error = "; ".join(result.diagnostics) or "validation failed"

        msg = f"failed to draft valid Terraform after 3 attempts: {last_error}"
        raise RuntimeError(msg)
```

## Callee: pickled_iac.cli._build_llm_client (hop 1)

```python
def _build_llm_client() -> LLMClient:
    factory = os.environ.get("PICKLED_IAC_LLM_FACTORY")
    if factory:
        module_name, sep, attr = factory.partition(":")
        if not sep:
            raise click.ClickException(
                "PICKLED_IAC_LLM_FACTORY must be 'module:callable'"
            )
        module = importlib.import_module(module_name)
        return cast(LLMClient, getattr(module, attr)())

    from pickled_core.llm.config import load_config
    from pickled_core.llm.factory import build_client

    provider = os.environ.get("PICKLED_LLM_PROVIDER", "anthropic")
    try:
        return build_client(provider, config=load_config())
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc
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

## Callee: pickled_iac.oracle.validate (hop 2)

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

## Unresolved callees

- `self._template.render` — protocol or unknown attribute type
- `hcl.splitlines` — method name matches multiple classes; receiver type not pinned
- `factory.partition` — variable 'factory' reassigned; type not stable
- `getattr(module, attr)()` — dynamic attribute access
- `getattr(module, attr)` — dynamic attribute access
