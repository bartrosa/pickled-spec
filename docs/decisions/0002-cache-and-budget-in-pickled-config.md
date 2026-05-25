# ADR-0002: Cache and budget in pickled.config.yaml

- **Status:** Accepted
- **Date:** 2026-05-19
- **Deciders:** pickled-spec contributors

## Context

`pickled-core` already ships disk-backed `LLMCache` and a `BudgetGuard` that
can cap cumulative LLM spend per process. Until now, leaf MCP servers and
package CLIs called `build_client(...)` directly without passing `cache=`, so
every `draft_*` and `validate_*` tool hit the live API on each rerun. No
bootstrap path installed a budget guard, so agent-driven loops had no
deterministic cost ceiling.

Dogfood workflows and Cursor-native MCP sessions repeat the same prompts
across iterations. Without wiring cache and budget at client construction,
token spend scales linearly with retries and a runaway tool loop can exhaust
quota before an operator notices.

## Decision drivers

- Reduce token cost on repeated dogfood runs without changing gate semantics.
- Provide an upper bound on runaway LLM loops in long-lived MCP processes.
- One construction path shared by bdd, schema, and iac (no duplicated factory
  parsing in each leaf).
- No new third-party dependencies; existing configs must keep working.
- Relative cache paths should stay stable when the repo root moves (resolve
  against the loaded YAML, not the shell CWD).

## Considered options

1. **Env vars only** — `PICKLED_CACHE_DIR`, `PICKLED_MAX_COST_USD`, etc., with
   no schema change. Rejected: easy to forget in docs; no single file checked
   into the repo for dogfood; harder to share defaults across teammates.

2. **YAML schema extension + env overrides (chosen)** — optional `cache:` and
   `budget:` blocks in `pickled.config.yaml`, with env winning on conflict.
   Central `build_default_client()` in `pickled-core` wires cache, budget, and
   provider; leaf `_build_llm_client()` functions delegate to it.

3. **Per-leaf YAML keys** — each package defines its own cache/budget section.
   Rejected: duplication, drift risk, and no shared semantics for
   `pickled-spec mcp` umbrella behavior.

## Decision outcome

Adopt option 2. Extend `PickledConfig` with `CacheSettings`, `BudgetSettings`,
and `source_path` (set by `load_config` when a file is read). Add
`build_default_client()` in `pickled_core.llm.bootstrap` that:

- Honors `PICKLED_*_LLM_FACTORY` for tests (no cache/budget wiring).
- Installs `BudgetGuard` when `budget.max_cost_usd` or `PICKLED_MAX_COST_USD`
  is set.
- Builds `LLMCache` unless cache mode is `off`.
- Passes the cache into `build_client(provider, config=cfg, cache=cache)`.

Leaf MCP CLIs (`pickled-bdd`, `pickled-schema`, `pickled-iac`) and
`pickled-bdd` CLI replace inline factory parsing with a single bootstrap call.

## Consequences

**Positive**

- Dogfood reruns can reuse cached completions (large reduction in repeat
  provider calls when inputs are unchanged).
- A configured `max_cost_usd` aborts further billed calls once the guard
  trips.
- Four copies of `_build_llm_client()` logic collapse to one helper.

**Negative**

- `PickledConfig` grows (`source_path`, `budget`); callers that construct
  configs manually must accept new defaults.

**Neutral**

- Configs without `cache:` / `budget:` behave as before: cache on at
  `.pickled-cache` (resolved next to the YAML), no budget cap.

## Path semantics

- Relative `cache.dir` resolves against the directory containing the loaded
  `pickled.config.yaml` (or XDG path), not the process CWD.
- `PICKLED_CACHE_DIR` overrides the directory and keeps **CWD-relative**
  resolution when the env value is relative (shell ergonomics).
- Absolute `cache.dir` values are unchanged.

## Future work

- Per-run budget reset for long-lived MCP servers (today the guard persists
  for the process lifetime).
- Programmatic cache invalidation API (delete by key prefix or provider).
- Optional YAML knob for budget reset cadence (per tool call vs per session).
