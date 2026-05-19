# pickled-core

Shared substrate for the **pickled-\*** family: immutable domain types, the
compensating **`Gate`** protocol, LLM client boundaries, MCP umbrella server,
and the **`pickled-spec`** umbrella CLI (`check-all`, `mcp`).

## What belongs here

- Cross-cutting **types** (`Verdict`, `GateResult`, draft outputs, etc.).
- The **`Gate`** interface every compensating gate implements.
- Thin infrastructure shared by multiple packages.

## What does not belong here

No DSL-specific parsers, no runner adapters, no product logic tied to Gherkin,
OpenAPI, Rego, or Terraform. Those live in **`pickled-bdd`**, **`pickled-schema`**,
and the other leaf packages.

## Consumers

End users normally install a domain package (for example **`pickled-bdd`**),
which depends on **`pickled-core`** transitively. You rarely install **pickled-core**
alone unless you are building a new family member.

## Monorepo context

This package lives in the **pickled-spec** monorepo. For the full pattern, package
matrix, and doc index, see the repository root [README](../../README.md).

## Umbrella CLI

When installed from this package (monorepo dev or `pickled-core` with scripts):

```bash
uv run pickled-spec check-all --workdir examples/user-management-crud/ --warn-ok
uv run pickled-spec mcp --transport stdio   # requires [mcp] extra
```

## Status

Pre-alpha; APIs may change between dev releases.

## Usage

`pickled-core` is rarely installed alone. End users install a leaf package
(e.g. `pickled-bdd`) which transitively pulls `pickled-core`.

For package authors building a new family member:

```python
from pickled_core import (
    Gate,  # gate protocol
    GateResult,
    LLMClient,  # LLM abstraction
    PickledMCPServer,  # MCP scaffolding
    PromptTemplate,
    Verdict,
)


class MyGate:
    name = "my-gate"

    def __init__(self, llm: LLMClient) -> None:
        self._llm = llm

    def run(self, target: object, *, context: dict[str, object] | None = None) -> GateResult:
        # ...
        return GateResult(gate_name=self.name, verdict=Verdict.PASS)
```

Implement **`Gate`** (a **`name`** and **`run(...)`** → **`GateResult`**). Use
**`PromptTemplate`** and **`LLMClient`** for LLM calls; register tools on
**`PickledMCPServer`** for MCP.
