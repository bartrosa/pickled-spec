# pickled-diff

**pickled-diff** compares a **candidate implementation** against a **reference
implementation** (oracle) across an **input corpus**, using pluggable runners and
comparators. It is the reference-oracle member of the **pickled-\*** family.

## Oracle category

Most family packages map to strong, medium, or weak deterministic backends.
**pickled-diff** adds a fourth category: **reference implementation as oracle** —
output equivalence on a sampled corpus against an existing trusted program.

That is stronger than weak oracles (which only check execution-shaped behaviour)
and weaker than strong oracles (no formal proof—agreement on the corpus only).
See [`docs/pattern.md`](../../docs/pattern.md).

## Status

Pre-alpha — APIs may change between dev releases.

## Development (from the monorepo)

```bash
uv sync
uv run pytest packages/pickled-diff/tests -v
uv run ruff check packages/pickled-diff
uv run mypy packages/pickled-core/src packages/pickled-diff/src
```

## CLI

```bash
uv run pickled-diff --help
```

| Command | Purpose |
|---------|---------|
| **`verify`** | Run `DifferentialOracleGate` with subprocess commands and a JSON corpus. Prints JSON; exit **0** / **1** / **2** for pass / warn / fail. |
| **`serve`** | Start stdio MCP with `verify_against_oracle`. |

### Example

```bash
uv run pickled-diff verify \
  --oracle "python packages/pickled-diff/examples/trivial_oracle.py" \
  --candidate "python packages/pickled-diff/examples/trivial_candidate.py" \
  --corpus packages/pickled-diff/examples/corpus.json
```

See [`examples/README.md`](examples/README.md).

## Library usage

```python
from pickled_diff import (
    CallableRunner,
    DifferentialOracleGate,
    ExactEqComparator,
    InMemoryCorpus,
)
from pickled_diff.corpus import CorpusItem

gate = DifferentialOracleGate(
    oracle=CallableRunner(lambda s: s.upper(), name="oracle"),
    candidate=CallableRunner(lambda s: s.upper(), name="candidate"),
    comparator=ExactEqComparator(),
)
result = gate.run(
    InMemoryCorpus([CorpusItem("greeting", "hi")]),
)
print(result.verdict, result.notes)
```

Domain-specific equivalence (tolerant numerics, AST shapes, and so on) belongs in
**consumer projects** as custom `Comparator` implementations.

## MCP tool registration

`pickled_diff.mcp_tools.register(server)` adds **`verify_against_oracle`** to a
`PickledMCPServer`. No LLM is required. Umbrella mounting is described in
[`docs/mcp.md`](../../docs/mcp.md).

## Monorepo context

Repository root [README](../../README.md) and [documentation index](../../docs/README.md).
