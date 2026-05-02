# MCP integration plan

Each package in the pickled family exposes its workflows to **Model Context
Protocol (MCP)** clients so interactive tools (Claude Desktop, Cursor, and
similar) can drive drafting, validation, and review steps without bespoke UI per
package.

## Goals

- End-to-end flows from chat: intent in natural language, artifact drafts,
  gate results, and iteration loops.
- One integration surface per deployment: clients speak MCP; packages register
  tools rather than shipping separate daemons per concern.

## Architecture

**Central server abstraction.** `pickled-core` defines a `PickledMCPServer` (name
final may vary in code) holding a **tool registry**, shared session context, and
hooks for auth and logging.

**Per-package registration.** Each package ships a `register(server)` (or
equivalent) function that adds tool definitions, input schemas, and handlers.
The root application composes the server once and calls each package’s
registrar in deterministic order.

No package reaches into another package’s handler internals; composition happens
only through core’s registry API.

## Transport and rollout

| Milestone | Behavior |
|-----------|----------|
| **v0.1** | Registry populated and unit-tested; **no** live MCP transport wired. |
| **v0.1.1** | **stdio** transport using the official **`mcp`** Python SDK, wiring the same registry. |

Later milestones may add HTTP or deployment-specific transports; they reuse the
same tool table.

## Initial tool surface (`pickled-bdd`)

Implemented in **`pickled_bdd.mcp_tools`** (v0.1): register with
**`register(server, llm=...)`**. Tool handlers take **keyword-only** arguments
matching their JSON Schema.

- **`draft_feature_from_story`** — argument **`story_text`** (string). Returns
  **`{ feature_text, rationale, warnings }`** from **`FeatureDrafter`**.

- **`validate_feature_ambiguity`** — argument **`feature_text`** (full Gherkin
  string). Parses via a temporary file (until a string parser exists), runs
  **`AmbiguityGate`**, returns **`{ verdict, notes, findings }`** (findings are
  structured like the **`pickled-bdd check`** JSON).

Future revisions may add optional parameters (e.g. style hints); v0.1 keeps the
surface minimal.

These tools deliberately stop short of executing arbitrary code or rewriting the
repository without explicit user action outside MCP.

## Out of scope for MCP tools here

The following belong in general-purpose agents or local scripts, not in the
pickled-spec tool surface:

- Running the **full** test suite or CI pipeline on behalf of the model.
- Writing or deleting arbitrary project files without human-controlled boundaries.
- Destructive git operations, credential handling, or cloud provisioning.

Pickled MCP tools focus on **DSL drafting**, **gate evaluation**, and **structured
feedback** aligned with the gate taxonomy.

## See also

- [`pattern.md`](pattern.md) — overall bridge structure.
- [`gates.md`](gates.md) — Ambiguity and future gates referenced by tools.
