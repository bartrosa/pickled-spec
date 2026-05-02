# pickled-bdd

**pickled-bdd** is the BDD-focused member of the **pickled-\*** family: an
**LLM-to-Gherkin** bridge with deterministic verification.

## DSL and runner

- **DSL:** [Gherkin](https://cucumber.io/docs/gherkin/) feature files.
- **Runner (v0.1):** [pytest-bdd](https://pytest-bdd.readthedocs.io/) — parsing and
  adapters target pytest-bdd semantics (for example, **Background** steps are merged
  into each scenario’s step list, matching runtime behaviour).

## Status

Pre-alpha — APIs and CLI evolve quickly.

## Quick start

Install from PyPI when published:

```bash
pip install pickled-bdd
```

A CLI for turning user stories into features lands in **PR-07**. Until then, parse
`.feature` files from Python via **`PytestBddAdapter.parse_feature_file`** (see docstrings).

## Monorepo

Developed inside [**pickled-spec**](https://github.com/bartrosa/pickled-spec). For the
shared architectural pattern, oracle strengths, gate taxonomy, and package matrix, read the
[**repository root README**](https://github.com/bartrosa/pickled-spec/blob/main/README.md).

## Documentation

See **`docs/pattern.md`** and **`docs/gates.md`** in the monorepo for how **pickled-bdd**
fits the weak-oracle + compensating-gates model.
