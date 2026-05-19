# Contributing

The full contributing guide lives at
[`docs/contributing.md`](docs/contributing.md).

Quick reference:

- `uv sync --extra mcp` to set up the workspace (MCP optional extra).
- `uv run pytest` to run tests.
- `uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok` for integration smoke.
- One PR per Goal; CI must be green.
- Conventional Commits in commit messages.
- ADRs for architectural decisions: see
  [`docs/decisions/`](docs/decisions/).
