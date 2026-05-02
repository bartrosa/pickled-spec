# pickled-policy

> **Status: planned, not yet implemented.**

This directory is a placeholder for the **policy** member of the pickled-\*
family. See [the monorepo roadmap](../../docs/roadmap.md) for the expected
timeline.

## What it will be

An **LLM-to-Rego / OPA** bridge for compliance and access policies: draft
policies from regulation text or business rules; compensating gates include
**Lawyer-in-the-loop** (mandatory human review for any policy encoding
regulation) and **Regression** (which policies are touched when a regulation
changes).

## Why it's not built yet

Regulatory-domain tooling carries asymmetric risk and needs the pattern proven
on lower-risk domains first. Likely the **v0.2** release alongside or instead of
**pickled-schema**, depending on user demand.

## Until then

This package is **not installable**. Track progress by watching the repository
or filing an issue under the **`pkg:policy`** label.
