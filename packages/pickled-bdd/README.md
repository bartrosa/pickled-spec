# pickled-bdd

**pickled-bdd** is the BDD-focused member of the **pickled-\*** family: an
**LLM-to-Gherkin** bridge with deterministic verification.

## DSL and runner

- **DSL:** [Gherkin](https://cucumber.io/docs/gherkin/) feature files.
- **Runner (v0.1):** [pytest-bdd](https://pytest-bdd.readthedocs.io/) — the
  **`PytestBddAdapter`** parser matches pytest-bdd behaviour (e.g. **Background**
  steps are prepended to each scenario at parse time, like the runner does at
  execution time).

## Status

Pre-alpha — APIs and CLI evolve quickly.

## Development (from the monorepo)

Clone [**pickled-spec**](https://github.com/bartrosa/pickled-spec), then from the
repo root:

```bash
uv sync
uv run pytest packages/pickled-bdd/tests
uv run ruff check packages/pickled-bdd
uv run mypy packages/pickled-core/src packages/pickled-bdd/src
```

Install the package in editable mode if you need it on `PATH` without `uv run`:

```bash
cd packages/pickled-bdd && uv pip install -e .
```

## CLI

The console script is **`pickled-bdd`**. In a dev clone, prefer:

```bash
uv run pickled-bdd --help
```

| Command | Purpose |
|--------|--------|
| **`draft <story.md>`** | Turn a user story (Markdown) into Gherkin. Use **`-o out.feature`** to write a file; default is stdout. |
| **`check <file.feature>`** | Run the compensating gate (default **`--gate ambiguity`**; **`all`** is accepted but maps to the same gate in v0.1). Prints JSON; exit **0** = pass, **1** = warn, **2** = fail. |
| **`serve`** | Build a **`PickledMCPServer`**, call **`pickled_bdd.mcp_tools.register`**, then **`serve()`** (still **NotImplementedError** until transport in v0.1.1). Confirms tool registration. |

### LLM backend

- **Default:** **`AnthropicClient`** (optional extra). Install with
  `pip install "pickled-core[anthropic]"` / resolve the extra in the workspace, and
  set **`ANTHROPIC_API_KEY`**.
- **Tests / CI / custom backends:** set **`PICKLED_BDD_LLM_FACTORY`** to
  **`module:callable`**, where the callable returns an **`LLMClient`** (e.g.
  `pickled_bdd.testing:build_fake_llm` for draft smoke, or
  `pickled_bdd.testing:build_check_pass_llm` for check without a real API).

### Example files (in this repo)

| Path | Role |
|------|------|
| `examples/password_reset.story.md` | User story for **`draft`**. |
| `examples/password_reset.feature` | Gherkin for **`check`**. |

```bash
# Draft (needs a real LLM unless you set PICKLED_BDD_LLM_FACTORY)
uv run pickled-bdd draft packages/pickled-bdd/examples/password_reset.story.md -o /tmp/out.feature

# Check ambiguity gate (same)
uv run pickled-bdd check packages/pickled-bdd/examples/password_reset.feature
```

## MCP tool registration

Package **`pickled_bdd.mcp_tools`** exposes **`register(server, llm=...)`**, which
adds **`draft_feature_from_story`** and **`validate_feature_ambiguity`** to the
registry on **`PickledMCPServer`**. Transport (stdio SDK) is described in the
monorepo [**`docs/mcp.md`**](../../docs/mcp.md).

## Monorepo context

Full pattern, gate taxonomy, and package matrix: [**repository root README**](https://github.com/bartrosa/pickled-spec/blob/main/README.md).

Conceptual fit (weak oracle, compensating gates): **`docs/pattern.md`** and
**`docs/gates.md`** in **pickled-spec**.

## Usage

### CLI

From the `packages/pickled-bdd` directory (paths match the package layout), or
invoke via `uv run pickled-bdd` with paths relative to the repo root.

Draft a feature from a story:

```bash
pickled-bdd draft examples/password_reset.story.md \
    -o examples/password_reset.feature
```

Check a feature for ambiguity:

```bash
pickled-bdd check examples/password_reset.feature
```

### Library

Install **`pickled-core[anthropic]`** if you use **`AnthropicClient`**. Set
**`ANTHROPIC_API_KEY`** in the environment.

```python
from pathlib import Path

from pickled_bdd import AmbiguityGate, FeatureDrafter, PytestBddAdapter
from pickled_core.llm.anthropic import AnthropicClient

llm = AnthropicClient()

# Draft
drafter = FeatureDrafter(llm)
result = drafter.draft_from_story(Path("examples/password_reset.story.md").read_text(encoding="utf-8"))
print(result.text)

# Check
feature = PytestBddAdapter().parse_feature_file(Path("examples/password_reset.feature"))
gate_result = AmbiguityGate(llm).run(feature)
print(gate_result.verdict, gate_result.notes)
```
