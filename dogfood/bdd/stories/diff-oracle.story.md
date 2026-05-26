# Story: pickled-diff verifies a candidate against an oracle on a corpus

## Context

Some classes of software are best verified by running them and
comparing the output to a known-good reference. Compilers, query
optimisers, parsers, serialisers, format converters, anything where
the answer is "for this input, the output is exactly X" and X is
either checkable against a previous version or against an
independent implementation. This is differential testing, and it
predates LLM-as-judge by decades: it is one of the few verification
strategies where the oracle is itself executable and deterministic.

`pickled-diff` packages that pattern. The user provides two
runners — a candidate (the implementation under test) and an oracle
(the reference) — plus a corpus of inputs. The gate runs both
runners on each input and compares the outputs. Any mismatch is a
verdict.

The design is intentionally minimal. There is no LLM in the path.
The comparator is either exact-string or structural-JSON; if a user
wants fuzzy semantic comparison they can plug in their own
comparator, but the project does not ship one. The runners are
either callables in the same Python process or subprocesses with
timeouts. Everything observable is deterministic in the absence of
test flakiness in the inputs themselves.

The corpus drafter is the one piece that touches the LLM. Given a
small set of seed examples, the drafter expands the corpus to a
target size, aiming for diversity — edge cases, boundary numerics,
unicode, empty inputs. The expanded corpus is returned as data; the
runner reads data, not LLM output, so test runs remain deterministic.

## What pickled-spec does today

`pickled-diff verify` (and `diff_verify_against_oracle` over MCP)
takes a candidate runner spec, an oracle runner spec, a corpus, and
a comparator name. It runs both runners on each corpus item in
sequence (no parallelism in v0.3), captures `OracleOutput(stdout,
exit_code, error)` from each, and applies the comparator.

Two comparators ship: `exact` and `structural_json`. Exact compares
stdout strings byte-for-byte. Structural-JSON parses both stdouts
as JSON and compares the parsed structures (so `{"a": 1, "b": 2}`
and `{"b": 2, "a": 1}` are equivalent). Comparator selection is an
explicit string, not auto-detected; ambiguity here would produce
silent verdicts.

Runners come in two shapes. `CallableRunner` wraps a
`Callable[[str], str]` for in-process testing. `SubprocessRunner`
spawns a subprocess command with `input_payload` on stdin,
captures stdout/stderr, and enforces a per-call timeout (default
30 seconds; configurable). A timeout produces `OracleOutput(stdout=
"", exit_code=-1, error="timeout after Xs")` and counts as a
divergence under any comparator.

The corpus drafter (`diff_draft_corpus_from_examples` over MCP)
takes a list of seed `{name, payload}` items, a target size, and
optional notes. The drafter prompts the model to produce a JSON
array of items of exact shape `{"name": str, "payload": str}`,
parsed and validated post-completion. Items that fail shape
validation are dropped with a warning; the corpus is returned
short with a `size mismatch` warning rather than padded with
fake data.

## What we want to verify

Across the CLI and MCP surfaces, with both comparators and both
runner shapes:

- A candidate that matches the oracle on every corpus item yields
  PASS, with one trace per item recording the matched output.
- A candidate that diverges on one item yields FAIL with the item
  name, the candidate's output, the oracle's output, and the
  comparator's verdict in the finding.
- A subprocess runner whose command times out produces a
  divergence with `exit_code=-1` and the timeout duration in the
  error string; the comparator treats this as a mismatch
  regardless of what the other runner returned.
- A subprocess runner whose command is not found
  (`FileNotFoundError`) produces a divergence with `exit_code=-1`
  and the OS error in the error string, not a Python traceback
  bubbling out of the gate.
- The structural-JSON comparator treats key ordering as
  insignificant and treats trailing whitespace differences in the
  serialised form as insignificant, while still flagging real
  structural divergence.
- The exact comparator treats every byte difference as a
  divergence, including trailing newlines.
- Comparator selection is a hard string match: an unknown
  comparator name yields a deterministic error before any runner
  executes, not after.
- The drafter emits a JSON array; items violating the
  `{name: str, payload: str}` shape are dropped with one warning
  per drop, and the corpus is returned at whatever size it ended
  up with.
- A drafter request for `target_size=N` that returns fewer or
  more than N valid items produces a `size mismatch` warning
  with both numbers; the corpus is still returned for the user to
  decide what to do.
- Identical drafter inputs (same seeds, same target_size, same
  notes) hit the disk cache.

## Inventory references

- CLI: `pickled-diff verify --candidate <X> --oracle <Y>
  --corpus <Z> --comparator <NAME>`,
  `pickled-diff draft-corpus --seeds <PATH|-> --target-size <N>`
- MCP tools: `diff_verify_against_oracle`,
  `diff_draft_corpus_from_examples`
- Gates: `DifferentialOracleGate` (class),
  `diff.verify_against_oracle` (entry point name)
- ADRs: ADR-0005 (LLM resolution for the drafter)

## Open questions

- Parallelism. Today runs are sequential. For corpora of a few
  hundred items this is fine; for thousands it dominates wall
  time. A `--workers N` flag is the obvious next step, but it
  changes the determinism guarantees in subtle ways (subprocess
  scheduling becomes nondeterministic; per-item timing telemetry
  becomes noisier). Candidate for v0.4, with a clear ADR on what
  guarantees parallelism preserves and which it relaxes.
- Comparator extensibility. Today the two ship comparators are
  hardcoded. Users with structural-but-not-JSON output (XML, CSV
  with semantic columns) have to write Python and depend on the
  internal API. A `pickled.diff.comparators` entry point would
  fit the project's existing convention (matching
  `pickled.gates`, `pickled.mcp.subservers`).
- The drafter does not enforce uniqueness on `name` across items.
  Two corpus items with the same `name` is a silent collision; the
  second shadows the first in any name-keyed downstream tooling.
  Candidate for a drafter-side validation warning.
- The `OracleOutput.stderr` field exists but no comparator
  inspects it. A "comparator that flags stderr divergence" is
  occasionally requested by users porting CLI tools; today they
  have to hand-roll it. Tracked as a future built-in.

## Status

draft
