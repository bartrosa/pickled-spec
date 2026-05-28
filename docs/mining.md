# Mining with `pickled-spec mine`

Mining turns a Python repository into a behavioural specification scaffold:
inventory of CLIs, MCP tools, and gates; user stories; Gherkin features;
rule tags; and gate evaluation reports. It works on **any** Python project
with discoverable Click entry points — not only this monorepo. The
`dogfood/` tree is one application of the same pipeline.

## Seven stages

| Stage | Command | Output |
|-------|---------|--------|
| 1. Inventory | `pickled-spec mine inventory <target>` | `inventory.json` |
| 2. Code | `pickled-spec mine code <target>` | `code-context/<surface-id>.md` |
| 3. Stories | `pickled-spec mine stories <target>` | `stories/*.story.md` |
| 4. Features | `pickled-spec mine features <target>` | `features/*.feature` |
| 5. Tag | `pickled-spec mine tag <target>` | `tags-proposals.json`, tags in features (quick mode) |
| 6. Evaluate | `pickled-spec mine evaluate <target>` | `evaluation/coverage.json`, `evaluation/ambiguity.json` |
| 7. Report | `pickled-spec mine report <target>` | `mining-report.md` |

Run the full pipeline:

```bash
pickled-spec mine all <target> --output ./mining-output/ --quick
```

Stages communicate through files under `--output`. Re-run any stage after
fixing inputs; use `--overwrite-stories` / `--overwrite-features` to
replace existing artifacts.

## Quick vs interactive

- **`--quick` (default):** parallel LLM calls where supported; tag stage
  writes the top proposal per scenario into feature files.
- **`--interactive`:** serial prompts for feature accept/skip/re-draft and
  per-scenario tag selection.

## `--surfaces` filter

Limit work to a subset of packages or surface ids (case-insensitive
substring match on package name **or** surface id):

```bash
# Only pickled-bdd surfaces
pickled-spec mine stories . --output /tmp/out --surfaces bdd

# bdd and rules packages
pickled-spec mine stories . --output /tmp/out --surfaces bdd,rules

# Any surface whose id contains "draft"
pickled-spec mine stories . --output /tmp/out --surfaces draft
```

The report notes when a filter was active. Use this to scope LLM-heavy
stages to a few packages instead of an entire monorepo.

## Code reading stage

`pickled-spec mine code` reads `inventory.json` and writes one markdown
file per surface under `code-context/`. It uses stdlib `ast` only (no extra
dependencies). The **stories** stage consumes these files when present.

```bash
pickled-spec mine inventory . --output /tmp/out
pickled-spec mine code . --output /tmp/out --depth callgraph --max-hops 2
pickled-spec mine stories . --output /tmp/out
```

| Flag | Default | Meaning |
|------|---------|---------|
| `--depth` | `body` | `signature`, `body`, or `callgraph` (expand callees) |
| `--callee-scope` | `same-package` | `self`, `same-package`, or `any-pickled` |
| `--max-hops` | `2` | Callee depth when `--depth callgraph` |
| `--max-callees` | `8` | Hard cap on collected units per surface |
| `--max-code-lines` | `400` | Hard cap on total source lines per surface |
| `--detect-cycles` | on | Write `code-context/_cycles.json` from observed edges |

Traversal uses a `visited` set (`module:qualname`) so mutual recursion
cannot loop forever. `--detect-cycles` is diagnostic only. Calls such as
`self._llm.complete(...)` on a Protocol-typed attribute are listed as
unresolved callees, not chased. Stdlib method noise (e.g. `.strip()`,
`Path.read_text()`) and decorator registration calls are omitted from the
unresolved list. See [ADR 0006](decisions/0006-mine-code-reading.md).

## Code-aware stories and drift detection

When `code-context/<surface-id>.md` exists, `mine stories` (and `mine all`
after the code stage) sends root source, resolved callee bodies, and
unresolved calls to the story prompt alongside the inventory docstring.

- Stories describe **observable behavior** (contract), not implementation
  detail (no line numbers or private method names in the behavior section).
- If the docstring **contradicts** the code, the model records bullets under
  **Open questions** as `Docstring drift: …` (code is source of truth).
- Without code-context, stories use docstring-only rules (Phase 8d).
- Metadata shows **Code depth**, **Units read**, and **Unresolved** counts.

Override the code-context directory:

```bash
pickled-spec mine stories . --output /tmp/out --code-context /path/to/code-context
```

See [ADR 0007](decisions/0007-code-aware-stories-and-drift.md).

## Rule sets

Tag and evaluate need YAML rule sets. Resolution order:

1. `--ruleset-config <path>` — parse `pickled.ruleset.yaml` at that path.
   Rule set paths inside the file are resolved **relative to the config
   file's directory** (same as `pickled-spec check-all`).
2. `--ruleset-dir <dir>` — load every `*.yaml` in that directory.
3. Otherwise `<target>/pickled.ruleset.yaml` if present.

Example (dogfood):

```bash
pickled-spec mine tag . \
  --output ./mining-output/ \
  --ruleset-config dogfood/pickled.ruleset.yaml
```

Paths like `./rulesets/pickled-internal.yaml` resolve under `dogfood/`, not
the shell cwd.

Optional `feature_glob:` in `pickled.ruleset.yaml` controls where
`check-all` and coverage evaluation find features (default
`features/**/*.feature`). See `packages/pickled-rules/README.md`.

## Output layout

```
mining-output/
  inventory.json
  code-context/
    <surface-id>.md
    _cycles.json
  stories/
    <surface-id>.story.md
  features/
    <surface-id>.feature
  tags-proposals.json
  evaluation/
    coverage.json
    ambiguity.json
  mining-report.md
  runs/
```

## LLM, cache, and performance

Stories and features call the LLM once per surface (unless skipped).
Without an API key or `pickled.config.yaml`, stories write placeholder
sections and the features stage is skipped.

- Use **`--surfaces`** to limit scope (e.g. `bdd` finishes in seconds on
  this monorepo vs tens of minutes for all surfaces).
- Use **`--max-parallel`** (default 4) to tune concurrent story/feature
  drafts in quick mode.
- Identical prompts hit the disk cache configured in `pickled.config.yaml`.

Inventory does not require an LLM. Evaluate runs ambiguity only when an
LLM is available; otherwise ambiguity is recorded as skipped (PASS with
note).

## Missing inputs

If a stage runs before its prerequisites, the CLI exits with code 2 and an
actionable message (no stack trace), for example:

```
stories requires inventory.json, which is produced by `pickled-spec mine inventory`.
```

## Worked example (small fixture)

```bash
FIXTURE=packages/pickled-core/tests/fixtures/tiny_target
OUT=/tmp/mine-demo

pickled-spec mine all "$FIXTURE" --output "$OUT" --quick --no-mcp
cat "$OUT/mining-report.md"
```

With an LLM configured, drop `--no-mcp` on a full repo and add
`--surfaces <package>` to keep story generation fast.

## Related docs

- [MCP integration](mcp.md) — umbrella server and subservers
- [ADR 0005](decisions/0005-pickled-spec-mine.md) — staged pipeline rationale
- [ADR 0006](decisions/0006-mine-code-reading.md) — code reading stage
