# Story: pickled-iac validates Terraform and runs an optional security baseline

## Context

Infrastructure-as-code is the most opinion-laden corner of a code
base. Half the value of any IaC tool is keeping the team from running
broken Terraform; the other half is keeping them from running
Terraform that creates a publicly-readable S3 bucket. The two checks
are independent and have different cost profiles: `terraform validate`
is fast and free, security scanning is slow and depends on a binary
that may or may not be installed.

`pickled-iac` separates these. The validate gate is mandatory when a
workspace ships any `*.tf` files. The security baseline is optional
— it runs only when Trivy is on PATH, and when it does run, only
HIGH and CRITICAL findings cause a non-PASS verdict; lower-severity
findings appear in notes but do not gate.

The wider design principle, codified in the
`verifier-warn-not-fail-on-skippable` rule, is that pickled-spec's
verdict ladder degrades gracefully. A missing optional binary must
not block the workspace; it must emit a WARN that surfaces the
skipped state without halting CI. This is the same principle as
AmbiguityGate's "PASS with note when no LLM" — make the skip
observable, but make it skip.

The reason the rule about Trivy (and the explicit prohibition on
tfsec and Terrascan) is a strict internal invariant rather than a
preference is that the deprecated tools are still common in
production CI pipelines. A team adopting pickled-spec must not be
quietly converted from Trivy to tfsec by a future contributor; the
rule pins the choice.

## What pickled-spec does today

The workspace runner registers two iac gates under the `pickled.gates`
entry point: `iac.validate` and `iac_security_baseline`.

`iac.validate` looks for `terraform` or `tofu` on PATH. If neither
is present, the verdict is WARN with a note `neither 'terraform' nor
'tofu' found on PATH`; this is observable in `check-all` output. If
one is present, it runs `terraform validate` (or `tofu validate`)
on every directory under `infra/` that contains a `*.tf` file.
Output goes into the gate's findings, one per error reported by the
binary.

`iac_security_baseline` looks for `trivy` on PATH. If absent, WARN
with `trivy not installed; security baseline skipped`. If present,
it runs `trivy config <dir>` on `infra/` and parses the JSON output.
HIGH and CRITICAL findings produce a FAIL verdict with one finding
entry per result; MEDIUM and LOW findings produce a PASS verdict
with the count in notes. Findings reference the file, the line
number, and the Trivy rule ID.

The MCP surfaces are `iac_validate_terraform_dir`,
`iac_security_baseline`, plus the LLM-backed advisors added in PR #3:
`iac_explain_plan_diff` and `iac_suggest_security_remediation`. The
deterministic gates do not touch the LLM; the advisor tools are
opt-in, agent-invoked, and not part of `check-all`.

## What we want to verify

Across the CLI and MCP surfaces:

- A workspace with clean Terraform under `infra/` and both
  `terraform` and `trivy` on PATH yields two PASS rows
  (`iac.validate`, `iac_security_baseline`) in `check-all` output.
- A workspace with no `infra/` directory yields PASS on both gates
  with notes indicating nothing to validate.
- A workspace with broken Terraform (syntax error in a `*.tf` file)
  yields FAIL on `iac.validate` with the binary's error message in
  the gate finding.
- With `terraform` missing but `tofu` on PATH, `iac.validate` runs
  `tofu validate` and emits PASS on clean code; the gate verdict
  must not change based on which acceptable binary was found.
- With neither binary on PATH, `iac.validate` emits WARN, not FAIL,
  and the verdict has a clear note explaining what was missing.
- With Trivy on PATH and a known-bad fixture (e.g. an S3 bucket
  with public read), `iac_security_baseline` emits FAIL with at
  least one finding whose severity is HIGH or CRITICAL.
- Without Trivy on PATH, `iac_security_baseline` emits WARN with a
  note explaining the skip; it never produces FAIL purely because
  the binary is absent.
- Findings include the file path, line number, and Trivy rule ID
  for each HIGH/CRITICAL issue.
- The strict internal invariant against tfsec and Terrascan is
  enforced at the package level: there is no code path in
  `pickled_iac` that invokes either binary, and the absence is
  observable by inspection of the package's source.

## Inventory references

- CLI: `pickled-iac validate <DIR>`, `pickled-iac security <DIR>`
- MCP tools: `iac_validate_terraform_dir`, `iac_security_baseline`,
  `iac_draft_terraform_module`, `iac_explain_plan_diff`,
  `iac_suggest_security_remediation`
- Gates: `iac.validate`, `iac_security_baseline` (entry point names)
- ADRs: none specific; the tfsec/Terrascan ban is documented in
  `pickled-internal.yaml` as `iac-trivy-not-tfsec-not-terrascan`

## Open questions

- Trivy's exit codes are not stable across versions. Today the gate
  parses Trivy's JSON output and ignores the binary's exit code,
  which is the right call but means a Trivy crash (non-zero exit,
  no parseable JSON on stdout) is currently misclassified as PASS.
  Candidate for a defensive "parse failed → WARN, not PASS"
  refinement.
- The WARN-on-missing-binary policy is consistent across
  `iac.validate` and `iac_security_baseline`, but inconsistent with
  AmbiguityGate (PASS-on-missing-LLM). Either consolidate by
  promoting all skippable gates to WARN, or document the asymmetry
  and explain it. Tracked under `verifier-warn-not-fail-on-skippable`.
- The advisor tools (`iac_explain_plan_diff`,
  `iac_suggest_security_remediation`) are excluded from `check-all`
  by design — they are interactive aids, not gates. This is the
  right call, but it means the advisor surface has no story
  coverage in `dogfood/`. Candidate for a future
  `iac-advisor.story.md` if the advisor pattern matures.

## Status

draft
