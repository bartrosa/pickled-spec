# ADR-0006: `pickled-spec mine code` static code reading

- **Status:** Accepted
- **Date:** 2026-05-28
- **Deciders:** pickled-spec contributors

## Context

Inventory and docstrings describe surfaces at a high level. For gates and CLIs
that delegate to helpers, the docstring often understates real behaviour
(temperature, validation, return shape). Phase 8e adds a dedicated **code**
stage that extracts source for each mined surface and, optionally, a bounded
set of intra-project callees.

## Decision drivers

- Ground later story generation in **observed code**, not names alone.
- Stay within stdlib (`ast` only): no grimp/pydeps dependency.
- Hard caps and a **visited** set so traversal cannot run away on cycles.
- Optional diagnostic cycle reporting without changing traversal semantics.

## Decision

Add `pickled-spec mine code` after inventory and before stories in `mine all`.

### Depth modes

| Mode | Content |
|------|---------|
| `signature` | Root signature, return annotation, docstring |
| `body` | Root full function/method body (default) |
| `callgraph` | Root body plus callee bodies up to `--max-hops` |

### Callee scope

- `self` — methods on the enclosing class (`self.helper()`).
- `same-package` — `self` plus same-package imports (default).
- `any-pickled` — same-package plus any `pickled_*` import.

### Bounds

- `--max-callees` (default 8) and `--max-code-lines` (default 400) per surface.
- `visited` keys (`module:qualname`) prevent re-expansion; this is the cycle
  safety mechanism.
- `--detect-cycles` runs a small DFS on collected edges and writes
  `code-context/_cycles.json` for the run log / report; it does not alter BFS.

### Output

`code-context/<surface-id>.md` per surface. Surfaces without a resolvable
definition (e.g. MCP tool names with no mapped callable) get a placeholder
file and the stage continues.

## Known limitations (v1)

- **Protocol / dynamic dispatch** — calls such as `self._llm.complete(...)`
  where `_llm` is a Protocol or opaque attribute are recorded as *unresolved*
  callees with a reason; they are not chased.
- **Python only** — no cross-language call graphs.
- **Static resolution only** — no runtime type inference or polymorphic targets.

Stories do not consume code-context until Phase 8f.

## Resolution patterns and limits (Phase 8e-fix)

Each collected callee records `resolution_kind` on the ref. Default
`--max-hops` is **2** so one delegation past the entry surface is included.

### Resolved kinds

| Kind | Pattern | Example |
|------|---------|---------|
| `free_function` | Same-module or imported callable | `helper()`, `chain.entry()` |
| `self_method` | `self.method()` on enclosing class | `self.helper()` |
| `constructor_method` | `Class(args).method()` | `Worker(cfg).process()` |
| `module_constructor` | `mod.Class(args).method()` | `mod.Worker(cfg).process()` |
| `annotated_param` | Parameter annotation pins type | `def f(w: Worker): w.m()` |
| `annotated_var` | Annotated local | `x: Worker = …; x.m()` |
| `assigned_constructor` | `x = Worker(); x.m()` (stable) | assignment tracking |

`@property`, `@staticmethod`, `@classmethod`, and `async def` bodies resolve
when the receiver type is known. Constructor arguments may contain separate
resolvable calls (e.g. `Worker(Builder(x).build()).process()`).

### Deliberately unresolved (reason strings)

| Reason | Pattern |
|--------|---------|
| `protocol or unknown attribute type` | `self._llm.complete()` (nested attribute on `self`) |
| `parameter '…' has no type annotation` | `def f(w): w.method()` |
| `receiver is a subscript expression` | `items[0].method()` |
| `variable '…' reassigned; type not stable` | `x = Worker(); x = Other(); x.m()` |
| `receiver is a conditional expression` | `(a if c else b).run()` |
| `receiver is a return value of unannotated callable` | `factory().build().run()`, `.process().finalize()` |
| `dynamic attribute access` | `getattr(obj, "m")()` |
| `method not found on class; possibly inherited (base not resolved in v1)` | method absent on declared class |
| Name collision / unknown receiver | two classes share method name, type not pinned |

Inherited methods (MRO) are not walked in v1. Return-type inference for
arbitrary call chains is out of scope. Traversal uses the same caps and
`visited` set as 8e; cycles are reported via `--detect-cycles` when enabled.

## Consequences

- `mine all` produces `code-context/` for downstream story prompts.
- Readers must pass inventory first; missing `inventory.json` raises an
  actionable error naming `mine inventory`.
