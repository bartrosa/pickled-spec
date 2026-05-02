# pickled-data

> **Status: planned, not yet implemented.**

This directory is a placeholder for the **data** member of the pickled-\*
family. See [the monorepo roadmap](../../docs/roadmap.md) for the expected
timeline.

## What it will be

An **LLM-to-SQL / dbt** bridge: draft schema migrations and dbt models from data
requirements; gates check that migrations apply cleanly, do not break existing
queries, and conform to naming conventions.

## Why it's not built yet

**v0.4+.** Database-specific tooling has many local variants (Postgres, MySQL,
Snowflake, BigQuery) that need careful scoping.

## Until then

This package is **not installable**. Track progress by watching the repository
or filing an issue under the **`pkg:data`** label.
