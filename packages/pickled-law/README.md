# pickled-law

> **Status: pre-alpha, PoC slice.**

`pickled-law` is the regulatory member of the pickled-* family. It loads
machine-readable corpora (YAML) describing regulations and provides
gates that verify whether project artifacts (Gherkin features, scenarios,
tests) cover the corpus appropriately.

## What ships in v0.1

- YAML corpus schema + loader.
- One reference corpus: HIPAA §164.312 Technical Safeguards.
- Coverage gate: detects corpus rules not cited by any scenario.
- CLI: `pickled-law check --corpus <name> --feature <path>` produces a
  Markdown Requirements Traceability Matrix.

## What is NOT in v0.1

See [`docs/roadmap.md`](../../docs/roadmap.md). High-level: no solver
backend, no conflict detection across corpora, no drift tracking, no
additional regulations beyond the HIPAA reference example.

## Roadmap and rationale

- [Roadmap section](../../docs/roadmap.md#pickled-law--regulatory-traceability) for what's coming.
- [ADR-0002](../../docs/adr/0002-pickled-law-package.md) for why `pickled-law` is a separate package from `pickled-policy`.

## License

Apache-2.0. The reference corpora ship under the same license; the
canonical regulatory text they reproduce is government-published and
not under copyright.
