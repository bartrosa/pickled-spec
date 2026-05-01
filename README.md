# pickled-spec

LLM-to-DSL bridge with deterministic verification — monorepo of the pickled-* family.
**Status:** pre-alpha. The full README lands in PR-01.
See [LICENSE](LICENSE).

Commits follow [Conventional Commits](https://www.conventionalcommits.org/); CI runs **gitlint**. Install the **commit-msg** hook (same rules as CI): `uv run pre-commit install --hook-type commit-msg`.

Cursor uses `.cursor/rules/conventional-commits.mdc` so agents default to Conventional Commits; the SCM “generate” button may still ignore rules sometimes—if it does, generate the subject in chat with `@Commit` or paste the diff.
