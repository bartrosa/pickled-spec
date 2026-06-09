"""CLI for pickled-iac."""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import click
from pickled_core import LLMClient, Verdict
from pickled_core.llm.bootstrap import build_default_client
from pickled_core.llm.config import ConfigError

from pickled_iac.drafter import IaCDrafter
from pickled_iac.gates import PlanDiffFinding, PlanDiffGate, SecurityBaselineGate
from pickled_iac.oracle import plan, validate
from pickled_iac.types import IaCToolMissingError


def _build_llm_client() -> LLMClient:
    """Build an LLM client honoring config, env, cache, and budget.

    Uses :func:`build_default_client` so the user's ``budget.max_cost_usd``
    cap (and disk cache) installed via ``pickled.config.yaml`` /
    ``PICKLED_MAX_COST_USD`` are actually enforced for ``pickled-iac draft``.
    """
    try:
        return build_default_client(factory_env="PICKLED_IAC_LLM_FACTORY")
    except ConfigError as exc:
        raise click.ClickException(str(exc)) from exc


@click.group()
@click.version_option(package_name="pickled-iac")
def main() -> None:
    """pickled-iac — Terraform drafting and verification."""


@main.command()
@click.argument("user_story")
@click.option("--provider", default="aws", show_default=True)
@click.option("-o", "--output", type=click.Path(file_okay=False, path_type=Path))
def draft(user_story: str, provider: str, output: Path | None) -> None:
    """Draft a Terraform module from a user story."""
    artifact = IaCDrafter(_build_llm_client()).draft_module(user_story, provider=provider)
    if output:
        output.mkdir(parents=True, exist_ok=True)
        (output / "main.tf").write_text(artifact.content, encoding="utf-8")
        click.echo(f"Wrote {output / 'main.tf'}", err=True)
    else:
        click.echo(artifact.content)


@main.command("validate")
@click.argument("tf_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
def validate_cmd(tf_dir: Path) -> None:
    """Run terraform validate on a directory."""
    try:
        result = validate(tf_dir)
    except IaCToolMissingError as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(
        json.dumps(
            {
                "valid": result.valid,
                "format": result.format,
                "diagnostics": result.diagnostics,
            },
            indent=2,
        )
    )
    if not result.valid:
        raise SystemExit(1)


@main.command()
@click.argument("tf_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
@click.option("-o", "--output", required=True, type=click.Path(path_type=Path))
def plan_cmd(tf_dir: Path, output: Path) -> None:
    """Run terraform plan and write JSON to *output*."""
    try:
        with tempfile.TemporaryDirectory() as tmp:
            plan_file = Path(tmp) / "plan.tfplan"
            result = plan(tf_dir, plan_file)
    except IaCToolMissingError as exc:
        raise click.ClickException(str(exc)) from exc
    output.write_text(json.dumps(result.plan_json, indent=2), encoding="utf-8")
    click.echo(f"Wrote plan JSON to {output}", err=True)


@main.command()
@click.option("--base", "base_path", required=True, type=click.Path(exists=True, path_type=Path))
@click.option("--head", "head_path", required=True, type=click.Path(exists=True, path_type=Path))
def diff(base_path: Path, head_path: Path) -> None:
    """Compare two terraform plan JSON files."""
    base_plan = json.loads(base_path.read_text(encoding="utf-8"))
    head_plan = json.loads(head_path.read_text(encoding="utf-8"))
    gate = PlanDiffGate()
    result = gate.run(head_plan, context={"base_plan": base_plan})
    click.echo(
        json.dumps(
            {
                "verdict": result.verdict.value,
                "notes": result.notes,
                "findings": [
                    {
                        "address": f.address,
                        "actions_before": list(f.actions_before),
                        "actions_after": list(f.actions_after),
                    }
                    for f in result.findings
                    if isinstance(f, PlanDiffFinding)
                ],
            },
            indent=2,
        )
    )
    if result.verdict is Verdict.FAIL:
        raise SystemExit(2)
    if result.verdict is Verdict.WARN:
        raise SystemExit(1)


@main.command()
@click.argument("tf_dir", type=click.Path(exists=True, file_okay=False, path_type=Path))
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


@main.group()
def mcp() -> None:
    """MCP server commands."""


@mcp.command("serve")
@click.option("--transport", type=click.Choice(["stdio", "http"]), default="stdio")
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def mcp_serve(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    from pickled_iac.mcp_cli import cli as mcp_cli_main

    mcp_cli_main.main(
        args=[
            "--transport",
            transport,
            *(["--host", host] if host else []),
            *(["--port", str(port)] if port is not None else []),
            *(["--allow-public"] if allow_public else []),
        ],
        standalone_mode=False,
    )


__all__ = ["main"]
