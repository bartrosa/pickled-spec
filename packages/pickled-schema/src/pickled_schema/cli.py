"""CLI for pickled-schema."""

from __future__ import annotations

import importlib
import json
import os
from pathlib import Path
from typing import cast

import click
from pickled_core import LLMClient, Verdict
from pickled_core.llm.config import ConfigError

from pickled_schema.gates import SchemaCoverageFinding, SchemaCoverageGate
from pickled_schema.json_schema.parser import load_json_schema_file
from pickled_schema.json_schema.validator import validate_json_schema_document
from pickled_schema.openapi.drafter import OpenAPIDrafter
from pickled_schema.openapi.parser import load_openapi_file
from pickled_schema.openapi.validator import validate_openapi_dict
from pickled_schema.proto.parser import parse_proto_file
from pickled_schema.types import SchemaArtifact, SchemaFormat


def _infer_format(path: Path) -> SchemaFormat:
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return SchemaFormat.openapi_3_1
    if suffix == ".json":
        return SchemaFormat.json_schema_2020_12
    if suffix == ".proto":
        return SchemaFormat.proto3
    msg = f"cannot infer format from extension {suffix!r}; use --format"
    raise click.ClickException(msg)


def _load_artifact(path: Path, fmt: SchemaFormat) -> SchemaArtifact:
    if fmt in (
        SchemaFormat.openapi_3_0,
        SchemaFormat.openapi_3_1,
        SchemaFormat.openapi_3_2,
    ):
        _, detected, artifact = load_openapi_file(path)
        return SchemaArtifact(
            format=detected,
            content=artifact.content,
            endpoint_id=artifact.endpoint_id,
            source=artifact.source,
        )
    if fmt is SchemaFormat.json_schema_2020_12:
        _, artifact = load_json_schema_file(path)
        return artifact
    if fmt is SchemaFormat.proto3:
        return parse_proto_file(path)
    raise click.ClickException(f"unsupported format {fmt!r}")


def _build_llm_client() -> LLMClient:
    factory = os.environ.get("PICKLED_SCHEMA_LLM_FACTORY")
    if factory:
        module_name, sep, attr = factory.partition(":")
        if not sep:
            raise click.ClickException(
                "PICKLED_SCHEMA_LLM_FACTORY must be 'module:callable'"
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


@click.group()
@click.version_option(package_name="pickled-schema")
def main() -> None:
    """pickled-schema — multi-format schema drafting and verification."""


@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
@click.option(
    "--format",
    "fmt",
    type=click.Choice([f.value for f in SchemaFormat]),
    default=None,
    help="Schema format (auto-detected from extension when omitted).",
)
def parse(file: Path, fmt: str | None) -> None:
    """Parse a schema file and print a short summary."""
    format_enum = SchemaFormat(fmt) if fmt else _infer_format(file)
    artifact = _load_artifact(file, format_enum)
    click.echo(
        json.dumps(
            {
                "format": artifact.format.value,
                "endpoint_id": artifact.endpoint_id,
                "source": artifact.source,
                "content_bytes": len(artifact.content.encode("utf-8")),
            },
            indent=2,
        )
    )


@main.command()
@click.argument("file", type=click.Path(exists=True, dir_okay=False, path_type=Path))
def validate(file: Path) -> None:
    """Validate a schema file against its format specification."""
    fmt = _infer_format(file)
    if fmt in (
        SchemaFormat.openapi_3_0,
        SchemaFormat.openapi_3_1,
        SchemaFormat.openapi_3_2,
    ):
        spec_dict, _, _ = load_openapi_file(file)
        validate_openapi_dict(spec_dict)
    elif fmt is SchemaFormat.json_schema_2020_12:
        schema_dict, _ = load_json_schema_file(file)
        validate_json_schema_document(schema_dict)
    elif fmt is SchemaFormat.proto3:
        parse_proto_file(file)
    click.echo(json.dumps({"valid": True, "format": fmt.value}))


@main.command()
@click.option(
    "--method",
    required=True,
    type=click.Choice(["GET", "POST", "PUT", "PATCH", "DELETE"]),
)
@click.option("--path", "endpoint_path", required=True)
@click.option(
    "--gherkin-file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
)
@click.option("-o", "--output", type=click.Path(dir_okay=False, path_type=Path))
def draft(
    method: str,
    endpoint_path: str,
    gherkin_file: Path,
    output: Path | None,
) -> None:
    """Draft an OpenAPI 3.1 path item from a Gherkin scenario."""
    gherkin = gherkin_file.read_text(encoding="utf-8")
    llm = _build_llm_client()
    artifact = OpenAPIDrafter(llm).draft_endpoint(
        method,
        endpoint_path,
        gherkin,
    )
    if output:
        output.write_text(artifact.content, encoding="utf-8")
        click.echo(f"Wrote {output}", err=True)
    else:
        click.echo(artifact.content)


def _resolve_feature_paths(
    feature_dir: Path | None,
    feature_glob: str | None,
) -> list[Path]:
    if feature_dir is not None and feature_glob is not None:
        raise click.ClickException("Use only one of --feature-dir or --feature-glob")
    if feature_dir is not None:
        return sorted(feature_dir.glob("**/*.feature"))
    if feature_glob is not None:
        from glob import glob

        return sorted(Path(p) for p in glob(feature_glob, recursive=True) if Path(p).is_file())
    raise click.ClickException("Provide --feature-dir or --feature-glob")


@main.command()
@click.option("--spec", required=True, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--feature-dir",
    default=None,
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    help="Directory tree containing .feature files.",
)
@click.option(
    "--feature-glob",
    default=None,
    help="Glob of .feature files (alternative to --feature-dir).",
)
def check(spec: Path, feature_dir: Path | None, feature_glob: str | None) -> None:
    """Run SchemaCoverageGate on @schema:endpoint tags in .feature files."""
    spec_dict, _, _ = load_openapi_file(spec)
    feature_paths = _resolve_feature_paths(feature_dir, feature_glob)
    if not feature_paths:
        raise click.ClickException("No feature files matched")
    gate = SchemaCoverageGate()
    result = gate.run(spec_dict, context={"feature_paths": feature_paths})
    payload = {
        "gate": result.gate_name,
        "verdict": result.verdict.value,
        "notes": result.notes,
        "findings": [
            {"tag": f.tag, "source": f.source}
            for f in result.findings
            if isinstance(f, SchemaCoverageFinding)
        ],
    }
    click.echo(json.dumps(payload, indent=2))
    if result.verdict is Verdict.FAIL:
        raise SystemExit(2)
    if result.verdict is Verdict.WARN:
        raise SystemExit(1)


@main.group()
def mcp() -> None:
    """MCP server commands."""


@mcp.command("serve")
@click.option(
    "--transport",
    type=click.Choice(["stdio", "http"]),
    default="stdio",
    show_default=True,
)
@click.option("--host", default=None)
@click.option("--port", type=int, default=None)
@click.option("--allow-public", is_flag=True, default=False)
def mcp_serve(
    transport: str,
    host: str | None,
    port: int | None,
    allow_public: bool,
) -> None:
    """Run the pickled-schema MCP server."""
    from pickled_schema.mcp_cli import cli as mcp_cli_main

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
