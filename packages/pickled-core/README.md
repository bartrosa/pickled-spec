# pickled-core

Shared substrate for the **pickled-\*** family: immutable domain types, the
compensating **`Gate`** protocol, and (in later releases) LLM client boundaries
and MCP server scaffolding used by sibling packages.

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

## Status

Pre-alpha; APIs may change between dev releases.

## Usage

`pickled-core` is rarely installed directly. End users install a sibling
package (e.g. `pickled-bdd`) which transitively pulls `pickled-core`.

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
