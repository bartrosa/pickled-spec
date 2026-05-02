# pickled-iac

> **Status: planned, not yet implemented.**

This directory is a placeholder for the **iac** member of the pickled-\*
family. See [the monorepo roadmap](../../docs/roadmap.md) for the expected
timeline.

## What it will be

An **LLM-to-Terraform / OpenTofu** bridge: draft infrastructure from intent
(e.g. “set up a load-balanced web app with a Postgres database”); gates use
`terraform plan` as the deterministic backend and check for drift against
deployed state.

## Why it's not built yet

**v0.3+.** Cloud provider authentication and state management add complexity
that is better tackled after the pattern is proven.

## Until then

This package is **not installable**. Track progress by watching the repository
or filing an issue under the **`pkg:iac`** label.
