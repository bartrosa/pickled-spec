# pickled-iac

**pickled-iac** drafts and verifies Terraform / OpenTofu modules with optional
Trivy config scanning.

## Status

Pre-alpha v0.1 — requires `terraform` or `tofu` on PATH for validate/plan/draft.
Trivy is optional (security gate skips with PASS + warning when absent).

## CLI

```bash
uv run pickled-iac draft "User story" --provider aws -o module/
uv run pickled-iac validate path/to/tf-dir
uv run pickled-iac plan path/to/tf-dir -o plan.json
uv run pickled-iac diff --base base.json --head head.json
uv run pickled-iac scan path/to/tf-dir
```

Security scanning uses **Trivy** only (no legacy Terraform scanner dependencies).

## MCP

Mounts as `iac_*` on the umbrella `pickled-spec mcp` server.
