# Examples

`ehr_authentication.feature` — a minimal Gherkin file demonstrating
citation tags for HIPAA §164.312. Used by PR-15's coverage gate end-to-end
test.

**Intentional gaps:** several corpus rules are deliberately **not** cited
by any scenario (e.g. Automatic Logoff, the Integrity standard, Transmission
Security). That omission is **by design** so the coverage gate can
demonstrate finding gaps. Do not “fix” the example by tagging every rule.

## Citation tag convention

Tags follow `@<corpus>:<rule_id>`, where:

- `<corpus>` is the lower-cased short name from `BUILTIN_CORPORA`
  (e.g. `hipaa`).
- `<rule_id>` is the corpus rule `id` field, copied verbatim
  (parentheses included).

Example: `@hipaa:(a)(2)(i)` cites HIPAA §164.312(a)(2)(i) Unique User
Identification.

A scenario can carry multiple citation tags. Citation tags coexist
with normal Gherkin tags; the coverage gate filters by the `<corpus>:`
prefix.
