# Mining report

Generated: `2026-05-28T15:14:17Z`
Target: `/Users/bartlomiejrosa/Projects/PORTFOLIO/pickled-spec`
Output: `/Users/bartlomiejrosa/Projects/PORTFOLIO/pickled-spec/dogfood/mining-output`

## Summary

- Packages: 7
- CLI commands: 46
- MCP tools: 19
- Gates: 16
- ADRs: 7
- Workspaces: 2

- Stories on disk: 72
- Features on disk: 72
- Tag proposals: yes
- Coverage evaluation: yes
- Ambiguity evaluation: yes

## Inventory highlights

| Package | CLI commands | MCP tools | Gates |
|---------|-------------:|----------:|------:|
| pickled-bdd | 6 | 2 | 2 |
| pickled-core | 11 | 0 | 0 |
| pickled-data | 6 | 4 | 3 |
| pickled-diff | 5 | 2 | 1 |
| pickled-iac | 7 | 5 | 4 |
| pickled-rules | 5 | 3 | 3 |
| pickled-schema | 6 | 3 | 3 |

### CLI commands

| Package | Command | Help |
|---------|---------|------|
| `pickled-bdd` | `ambiguity` | Run the ambiguity gate (alias for ``check --gate ambiguity``). |
| `pickled-bdd` | `check` | Run compensating gates against a .feature file. |
| `pickled-bdd` | `draft` | Draft a .feature file from a user story (Markdown). |
| `pickled-bdd` | `mcp` | MCP server commands. |
| `pickled-bdd` | `mcp serve` | Run the pickled-bdd MCP server. |
| `pickled-bdd` | `serve` | Deprecated alias for ``pickled-bdd mcp serve``. |
| `pickled-core` | `check-all` | Run workspace gates from every pickled-* package against a directory. |
| `pickled-core` | `mcp` | Run the umbrella MCP server (all family packages mounted). |
| `pickled-core` | `mine` | Mine a Python project for surfaces, stories, features, and gate results. |
| `pickled-core` | `mine all` | Run inventory → code → stories → features → tag → evaluate → report. |
| `pickled-core` | `mine code` | Stage 2: extract code context per surface from inventory.json. |
| `pickled-core` | `mine evaluate` | Stage 6: evaluate coverage and ambiguity gates. |
| `pickled-core` | `mine features` | Stage 4: draft features from stories. |
| `pickled-core` | `mine inventory` | Stage 1: introspect target and write inventory.json. |
| `pickled-core` | `mine report` | Stage 7: render mining-report.md from pipeline outputs. |
| `pickled-core` | `mine stories` | Stage 3: emit stories from inventory.json. |
| `pickled-core` | `mine tag` | Stage 5: tag scenarios in generated features. |
| `pickled-data` | `apply` | Apply migration to in-memory SQLite and print resulting schema. |
| `pickled-data` | `check-drift` | Run MigrationDriftGate against expected schema YAML. |
| `pickled-data` | `draft` | Draft a SQL migration from a natural-language intent. |
| `pickled-data` | `mcp` | MCP server commands. |
| `pickled-data` | `mcp serve` |  |
| `pickled-data` | `parse` | Parse a migration SQL file and print AST summary. |
| `pickled-diff` | `draft-corpus` | Expand seed examples into a larger differential corpus. |
| `pickled-diff` | `mcp` | MCP server commands. |
| `pickled-diff` | `mcp serve` | Run the pickled-diff MCP server. |
| `pickled-diff` | `serve` | Deprecated alias for ``pickled-diff mcp serve``. |
| `pickled-diff` | `verify` | Compare candidate vs reference across a JSON input corpus. |
| `pickled-iac` | `diff` | Compare two terraform plan JSON files. |
| `pickled-iac` | `draft` | Draft a Terraform module from a user story. |
| `pickled-iac` | `mcp` | MCP server commands. |
| `pickled-iac` | `mcp serve` |  |
| `pickled-iac` | `plan-cmd` | Run terraform plan and write JSON to *output*. |
| `pickled-iac` | `scan` | Run Trivy config scan (optional; skips if trivy missing). |
| `pickled-iac` | `validate` | Run terraform validate on a directory. |
| `pickled-rules` | `check` | Check feature coverage against a YAML rule set. |
| `pickled-rules` | `draft` | Draft a YAML rule set from a natural-language brief. |
| `pickled-rules` | `list-rules` | List rule ids from a YAML rule set. |
| `pickled-rules` | `mcp` | MCP server commands. |
| `pickled-rules` | `mcp serve` | Run the pickled-rules MCP server. |
| `pickled-schema` | `check` | Run SchemaCoverageGate on @schema:endpoint tags in .feature files. |
| `pickled-schema` | `draft` | Draft an OpenAPI 3.1 path item from a Gherkin scenario. |
| `pickled-schema` | `mcp` | MCP server commands. |
| `pickled-schema` | `mcp serve` | Run the pickled-schema MCP server. |
| `pickled-schema` | `parse` | Parse a schema file and print a short summary. |
| `pickled-schema` | `validate` | Validate a schema file against its format specification. |

## Stories generated

| Surface | Path |
|---------|------|
| bdd_draft_feature_from_story.story | `stories/bdd_draft_feature_from_story.story.md` |
| bdd_validate_feature_ambiguity.story | `stories/bdd_validate_feature_ambiguity.story.md` |
| data_apply_sql_to_sandbox.story | `stories/data_apply_sql_to_sandbox.story.md` |
| data_check_migration_drift.story | `stories/data_check_migration_drift.story.md` |
| data_draft_sql_migration_from_intent.story | `stories/data_draft_sql_migration_from_intent.story.md` |
| data_parse_sql_migration.story | `stories/data_parse_sql_migration.story.md` |
| diff_draft_corpus_from_examples.story | `stories/diff_draft_corpus_from_examples.story.md` |
| diff_verify_against_oracle.story | `stories/diff_verify_against_oracle.story.md` |
| iac_diff_terraform_plans.story | `stories/iac_diff_terraform_plans.story.md` |
| iac_draft_terraform_module.story | `stories/iac_draft_terraform_module.story.md` |
| iac_explain_plan_diff.story | `stories/iac_explain_plan_diff.story.md` |
| iac_suggest_security_remediation.story | `stories/iac_suggest_security_remediation.story.md` |
| iac_validate_terraform_dir.story | `stories/iac_validate_terraform_dir.story.md` |
| pickled_bdd_ambiguity.story | `stories/pickled_bdd_ambiguity.story.md` |
| pickled_bdd_ambiguitygate.story | `stories/pickled_bdd_ambiguitygate.story.md` |
| pickled_bdd_check.story | `stories/pickled_bdd_check.story.md` |
| pickled_bdd_draft.story | `stories/pickled_bdd_draft.story.md` |
| pickled_bdd_mcp.story | `stories/pickled_bdd_mcp.story.md` |
| pickled_bdd_run_all.story | `stories/pickled_bdd_run_all.story.md` |
| pickled_core_check_all.story | `stories/pickled_core_check_all.story.md` |
| pickled_core_mine.story | `stories/pickled_core_mine.story.md` |
| pickled_core_mine_all.story | `stories/pickled_core_mine_all.story.md` |
| pickled_core_mine_code.story | `stories/pickled_core_mine_code.story.md` |
| pickled_core_mine_evaluate.story | `stories/pickled_core_mine_evaluate.story.md` |
| pickled_core_mine_features.story | `stories/pickled_core_mine_features.story.md` |
| pickled_core_mine_inventory.story | `stories/pickled_core_mine_inventory.story.md` |
| pickled_core_mine_report.story | `stories/pickled_core_mine_report.story.md` |
| pickled_core_mine_stories.story | `stories/pickled_core_mine_stories.story.md` |
| pickled_core_mine_tag.story | `stories/pickled_core_mine_tag.story.md` |
| pickled_data_apply.story | `stories/pickled_data_apply.story.md` |
| pickled_data_check_drift.story | `stories/pickled_data_check_drift.story.md` |
| pickled_data_datacontractgate.story | `stories/pickled_data_datacontractgate.story.md` |
| pickled_data_draft.story | `stories/pickled_data_draft.story.md` |
| pickled_data_mcp.story | `stories/pickled_data_mcp.story.md` |
| pickled_data_migrationdriftgate.story | `stories/pickled_data_migrationdriftgate.story.md` |
| pickled_data_parse.story | `stories/pickled_data_parse.story.md` |
| pickled_data_run_all.story | `stories/pickled_data_run_all.story.md` |
| pickled_diff_draft_corpus.story | `stories/pickled_diff_draft_corpus.story.md` |
| pickled_diff_mcp.story | `stories/pickled_diff_mcp.story.md` |
| pickled_diff_run_all.story | `stories/pickled_diff_run_all.story.md` |
| pickled_diff_verify.story | `stories/pickled_diff_verify.story.md` |
| pickled_iac_diff.story | `stories/pickled_iac_diff.story.md` |
| pickled_iac_draft.story | `stories/pickled_iac_draft.story.md` |
| pickled_iac_iacambiguitygate.story | `stories/pickled_iac_iacambiguitygate.story.md` |
| pickled_iac_mcp.story | `stories/pickled_iac_mcp.story.md` |
| pickled_iac_plan_cmd.story | `stories/pickled_iac_plan_cmd.story.md` |
| pickled_iac_plandiffgate.story | `stories/pickled_iac_plandiffgate.story.md` |
| pickled_iac_run_all.story | `stories/pickled_iac_run_all.story.md` |
| pickled_iac_scan.story | `stories/pickled_iac_scan.story.md` |
| pickled_iac_securitybaselinegate.story | `stories/pickled_iac_securitybaselinegate.story.md` |
| pickled_iac_validate.story | `stories/pickled_iac_validate.story.md` |
| pickled_rules_check.story | `stories/pickled_rules_check.story.md` |
| pickled_rules_coverage_gate.story | `stories/pickled_rules_coverage_gate.story.md` |
| pickled_rules_coverage_gate_features.story | `stories/pickled_rules_coverage_gate_features.story.md` |
| pickled_rules_draft.story | `stories/pickled_rules_draft.story.md` |
| pickled_rules_list_rules.story | `stories/pickled_rules_list_rules.story.md` |
| pickled_rules_mcp.story | `stories/pickled_rules_mcp.story.md` |
| pickled_rules_run_all.story | `stories/pickled_rules_run_all.story.md` |
| pickled_schema_check.story | `stories/pickled_schema_check.story.md` |
| pickled_schema_draft.story | `stories/pickled_schema_draft.story.md` |
| pickled_schema_mcp.story | `stories/pickled_schema_mcp.story.md` |
| pickled_schema_parse.story | `stories/pickled_schema_parse.story.md` |
| pickled_schema_run_all.story | `stories/pickled_schema_run_all.story.md` |
| pickled_schema_schemaambiguitygate.story | `stories/pickled_schema_schemaambiguitygate.story.md` |
| pickled_schema_schemacoveragegate.story | `stories/pickled_schema_schemacoveragegate.story.md` |
| pickled_schema_validate.story | `stories/pickled_schema_validate.story.md` |
| rules_check_ruleset_coverage.story | `stories/rules_check_ruleset_coverage.story.md` |
| rules_draft_ruleset_from_brief.story | `stories/rules_draft_ruleset_from_brief.story.md` |
| rules_list_rules.story | `stories/rules_list_rules.story.md` |
| schema_check_schema_coverage.story | `stories/schema_check_schema_coverage.story.md` |
| schema_draft_openapi_endpoint.story | `stories/schema_draft_openapi_endpoint.story.md` |
| schema_validate_openapi_spec.story | `stories/schema_validate_openapi_spec.story.md` |

## Tag proposals

- `features/bdd_draft_feature_from_story.feature`: 8 scenario(s)
- `features/bdd_validate_feature_ambiguity.feature`: 7 scenario(s)
- `features/data_apply_sql_to_sandbox.feature`: 8 scenario(s)
- `features/data_check_migration_drift.feature`: 8 scenario(s)
- `features/data_draft_sql_migration_from_intent.feature`: 11 scenario(s)
- `features/data_parse_sql_migration.feature`: 10 scenario(s)
- `features/diff_draft_corpus_from_examples.feature`: 6 scenario(s)
- `features/diff_verify_against_oracle.feature`: 7 scenario(s)
- `features/iac_diff_terraform_plans.feature`: 9 scenario(s)
- `features/iac_draft_terraform_module.feature`: 11 scenario(s)
- `features/iac_explain_plan_diff.feature`: 9 scenario(s)
- `features/iac_suggest_security_remediation.feature`: 7 scenario(s)
- `features/iac_validate_terraform_dir.feature`: 7 scenario(s)
- `features/pickled_bdd_ambiguity.feature`: 10 scenario(s)
- `features/pickled_bdd_ambiguitygate.feature`: 11 scenario(s)
- `features/pickled_bdd_check.feature`: 8 scenario(s)
- `features/pickled_bdd_draft.feature`: 7 scenario(s)
- `features/pickled_bdd_mcp.feature`: 3 scenario(s)
- `features/pickled_bdd_run_all.feature`: 8 scenario(s)
- `features/pickled_core_check_all.feature`: 10 scenario(s)
- `features/pickled_core_mine.feature`: 6 scenario(s)
- `features/pickled_core_mine_all.feature`: 12 scenario(s)
- `features/pickled_core_mine_code.feature`: 13 scenario(s)
- `features/pickled_core_mine_evaluate.feature`: 11 scenario(s)
- `features/pickled_core_mine_features.feature`: 10 scenario(s)
- `features/pickled_core_mine_inventory.feature`: 8 scenario(s)
- `features/pickled_core_mine_report.feature`: 7 scenario(s)
- `features/pickled_core_mine_stories.feature`: 14 scenario(s)
- `features/pickled_core_mine_tag.feature`: 9 scenario(s)
- `features/pickled_data_apply.feature`: 19 scenario(s)
- `features/pickled_data_check_drift.feature`: 7 scenario(s)
- `features/pickled_data_datacontractgate.feature`: 12 scenario(s)
- `features/pickled_data_draft.feature`: 17 scenario(s)
- `features/pickled_data_mcp.feature`: 5 scenario(s)
- `features/pickled_data_migrationdriftgate.feature`: 18 scenario(s)
- `features/pickled_data_parse.feature`: 8 scenario(s)
- `features/pickled_data_run_all.feature`: 15 scenario(s)
- `features/pickled_diff_draft_corpus.feature`: 8 scenario(s)
- `features/pickled_diff_mcp.feature`: 3 scenario(s)
- `features/pickled_diff_run_all.feature`: 11 scenario(s)
- `features/pickled_diff_verify.feature`: 17 scenario(s)
- `features/pickled_iac_diff.feature`: 19 scenario(s)
- `features/pickled_iac_draft.feature`: 14 scenario(s)
- `features/pickled_iac_iacambiguitygate.feature`: 14 scenario(s)
- `features/pickled_iac_mcp.feature`: 6 scenario(s)
- `features/pickled_iac_plan_cmd.feature`: 6 scenario(s)
- `features/pickled_iac_plandiffgate.feature`: 25 scenario(s)
- `features/pickled_iac_run_all.feature`: 14 scenario(s)
- `features/pickled_iac_scan.feature`: 10 scenario(s)
- `features/pickled_iac_securitybaselinegate.feature`: 13 scenario(s)
- `features/pickled_iac_validate.feature`: 6 scenario(s)
- `features/pickled_rules_check.feature`: 20 scenario(s)
- `features/pickled_rules_coverage_gate.feature`: 14 scenario(s)
- `features/pickled_rules_coverage_gate_features.feature`: 12 scenario(s)
- `features/pickled_rules_draft.feature`: 13 scenario(s)
- `features/pickled_rules_list_rules.feature`: 6 scenario(s)
- `features/pickled_rules_mcp.feature`: 3 scenario(s)
- `features/pickled_rules_run_all.feature`: 19 scenario(s)
- `features/pickled_schema_check.feature`: 14 scenario(s)
- `features/pickled_schema_draft.feature`: 19 scenario(s)
- `features/pickled_schema_mcp.feature`: 2 scenario(s)
- `features/pickled_schema_parse.feature`: 10 scenario(s)
- `features/pickled_schema_run_all.feature`: 22 scenario(s)
- `features/pickled_schema_schemaambiguitygate.feature`: 14 scenario(s)
- `features/pickled_schema_schemacoveragegate.feature`: 23 scenario(s)
- `features/pickled_schema_validate.feature`: 14 scenario(s)
- `features/rules_check_ruleset_coverage.feature`: 7 scenario(s)
- `features/rules_draft_ruleset_from_brief.feature`: 8 scenario(s)
- `features/rules_list_rules.feature`: 7 scenario(s)
- `features/schema_check_schema_coverage.feature`: 7 scenario(s)
- `features/schema_draft_openapi_endpoint.feature`: 8 scenario(s)
- `features/schema_validate_openapi_spec.feature`: 5 scenario(s)

## Features generated

| Surface | Scenarios | Path |
|---------|----------:|------|
| bdd_draft_feature_from_story | 8 | `features/bdd_draft_feature_from_story.feature` |
| bdd_validate_feature_ambiguity | 6 | `features/bdd_validate_feature_ambiguity.feature` |
| data_apply_sql_to_sandbox | 6 | `features/data_apply_sql_to_sandbox.feature` |
| data_check_migration_drift | 7 | `features/data_check_migration_drift.feature` |
| data_draft_sql_migration_from_intent | 10 | `features/data_draft_sql_migration_from_intent.feature` |
| data_parse_sql_migration | 9 | `features/data_parse_sql_migration.feature` |
| diff_draft_corpus_from_examples | 5 | `features/diff_draft_corpus_from_examples.feature` |
| diff_verify_against_oracle | 6 | `features/diff_verify_against_oracle.feature` |
| iac_diff_terraform_plans | 8 | `features/iac_diff_terraform_plans.feature` |
| iac_draft_terraform_module | 9 | `features/iac_draft_terraform_module.feature` |
| iac_explain_plan_diff | 9 | `features/iac_explain_plan_diff.feature` |
| iac_suggest_security_remediation | 7 | `features/iac_suggest_security_remediation.feature` |
| iac_validate_terraform_dir | 7 | `features/iac_validate_terraform_dir.feature` |
| pickled_bdd_ambiguity | 8 | `features/pickled_bdd_ambiguity.feature` |
| pickled_bdd_ambiguitygate | 10 | `features/pickled_bdd_ambiguitygate.feature` |
| pickled_bdd_check | 7 | `features/pickled_bdd_check.feature` |
| pickled_bdd_draft | 7 | `features/pickled_bdd_draft.feature` |
| pickled_bdd_mcp | 3 | `features/pickled_bdd_mcp.feature` |
| pickled_bdd_run_all | 7 | `features/pickled_bdd_run_all.feature` |
| pickled_core_check_all | 10 | `features/pickled_core_check_all.feature` |
| pickled_core_mine | 6 | `features/pickled_core_mine.feature` |
| pickled_core_mine_all | 11 | `features/pickled_core_mine_all.feature` |
| pickled_core_mine_code | 12 | `features/pickled_core_mine_code.feature` |
| pickled_core_mine_evaluate | 10 | `features/pickled_core_mine_evaluate.feature` |
| pickled_core_mine_features | 9 | `features/pickled_core_mine_features.feature` |
| pickled_core_mine_inventory | 7 | `features/pickled_core_mine_inventory.feature` |
| pickled_core_mine_report | 6 | `features/pickled_core_mine_report.feature` |
| pickled_core_mine_stories | 13 | `features/pickled_core_mine_stories.feature` |
| pickled_core_mine_tag | 8 | `features/pickled_core_mine_tag.feature` |
| pickled_data_apply | 19 | `features/pickled_data_apply.feature` |
| pickled_data_check_drift | 7 | `features/pickled_data_check_drift.feature` |
| pickled_data_datacontractgate | 11 | `features/pickled_data_datacontractgate.feature` |
| pickled_data_draft | 16 | `features/pickled_data_draft.feature` |
| pickled_data_mcp | 5 | `features/pickled_data_mcp.feature` |
| pickled_data_migrationdriftgate | 18 | `features/pickled_data_migrationdriftgate.feature` |
| pickled_data_parse | 7 | `features/pickled_data_parse.feature` |
| pickled_data_run_all | 13 | `features/pickled_data_run_all.feature` |
| pickled_diff_draft_corpus | 8 | `features/pickled_diff_draft_corpus.feature` |
| pickled_diff_mcp | 3 | `features/pickled_diff_mcp.feature` |
| pickled_diff_run_all | 8 | `features/pickled_diff_run_all.feature` |
| pickled_diff_verify | 15 | `features/pickled_diff_verify.feature` |
| pickled_iac_diff | 18 | `features/pickled_iac_diff.feature` |
| pickled_iac_draft | 13 | `features/pickled_iac_draft.feature` |
| pickled_iac_iacambiguitygate | 13 | `features/pickled_iac_iacambiguitygate.feature` |
| pickled_iac_mcp | 6 | `features/pickled_iac_mcp.feature` |
| pickled_iac_plan_cmd | 5 | `features/pickled_iac_plan_cmd.feature` |
| pickled_iac_plandiffgate | 24 | `features/pickled_iac_plandiffgate.feature` |
| pickled_iac_run_all | 14 | `features/pickled_iac_run_all.feature` |
| pickled_iac_scan | 9 | `features/pickled_iac_scan.feature` |
| pickled_iac_securitybaselinegate | 11 | `features/pickled_iac_securitybaselinegate.feature` |
| pickled_iac_validate | 6 | `features/pickled_iac_validate.feature` |
| pickled_rules_check | 19 | `features/pickled_rules_check.feature` |
| pickled_rules_coverage_gate | 14 | `features/pickled_rules_coverage_gate.feature` |
| pickled_rules_coverage_gate_features | 12 | `features/pickled_rules_coverage_gate_features.feature` |
| pickled_rules_draft | 13 | `features/pickled_rules_draft.feature` |
| pickled_rules_list_rules | 5 | `features/pickled_rules_list_rules.feature` |
| pickled_rules_mcp | 3 | `features/pickled_rules_mcp.feature` |
| pickled_rules_run_all | 19 | `features/pickled_rules_run_all.feature` |
| pickled_schema_check | 13 | `features/pickled_schema_check.feature` |
| pickled_schema_draft | 19 | `features/pickled_schema_draft.feature` |
| pickled_schema_mcp | 2 | `features/pickled_schema_mcp.feature` |
| pickled_schema_parse | 9 | `features/pickled_schema_parse.feature` |
| pickled_schema_run_all | 21 | `features/pickled_schema_run_all.feature` |
| pickled_schema_schemaambiguitygate | 11 | `features/pickled_schema_schemaambiguitygate.feature` |
| pickled_schema_schemacoveragegate | 23 | `features/pickled_schema_schemacoveragegate.feature` |
| pickled_schema_validate | 13 | `features/pickled_schema_validate.feature` |
| rules_check_ruleset_coverage | 6 | `features/rules_check_ruleset_coverage.feature` |
| rules_draft_ruleset_from_brief | 7 | `features/rules_draft_ruleset_from_brief.feature` |
| rules_list_rules | 6 | `features/rules_list_rules.feature` |
| schema_check_schema_coverage | 7 | `features/schema_check_schema_coverage.feature` |
| schema_draft_openapi_endpoint | 7 | `features/schema_draft_openapi_endpoint.feature` |
| schema_validate_openapi_spec | 5 | `features/schema_validate_openapi_spec.feature` |

## Coverage by rule set

| Rule set | Verdict | Unreferenced strict |
|----------|---------|--------------------:|
| pickled-internal | pass | 0 |
| best-practices | pass | 0 |
| oss-hygiene | pass | 0 |
| bdd-domain | fail | 1 |

Unreferenced strict rules in `bdd-domain`:
- `gherkin-then-asserts-observable-outcome`

| rules-domain | pass | 0 |
| schema-domain | pass | 0 |
| iac-domain | pass | 0 |
| data-domain | pass | 0 |
| diff-domain | pass | 0 |
| core-domain | pass | 0 |

## Ambiguity by feature

| Feature | Verdict | Findings | Skipped |
|---------|---------|----------:|---------|
| `features/bdd_draft_feature_from_story.feature` | fail | 8 | no |
| `features/bdd_validate_feature_ambiguity.feature` | fail | 12 | no |
| `features/data_apply_sql_to_sandbox.feature` | fail | 13 | no |
| `features/data_check_migration_drift.feature` | fail | 11 | no |
| `features/data_draft_sql_migration_from_intent.feature` | fail | 13 | no |
| `features/data_parse_sql_migration.feature` | fail | 14 | no |
| `features/diff_draft_corpus_from_examples.feature` | fail | 9 | no |
| `features/diff_verify_against_oracle.feature` | fail | 9 | no |
| `features/iac_diff_terraform_plans.feature` | fail | 14 | no |
| `features/iac_draft_terraform_module.feature` | fail | 15 | no |
| `features/iac_explain_plan_diff.feature` | fail | 9 | no |
| `features/iac_suggest_security_remediation.feature` | fail | 7 | no |
| `features/iac_validate_terraform_dir.feature` | fail | 7 | no |
| `features/pickled_bdd_ambiguity.feature` | fail | 14 | no |
| `features/pickled_bdd_ambiguitygate.feature` | warn | 12 | no |
| `features/pickled_bdd_check.feature` | fail | 12 | no |
| `features/pickled_bdd_draft.feature` | fail | 7 | no |
| `features/pickled_bdd_mcp.feature` | fail | 3 | no |
| `features/pickled_bdd_run_all.feature` | fail | 10 | no |
| `features/pickled_core_check_all.feature` | fail | 10 | no |
| `features/pickled_core_mine.feature` | fail | 6 | no |
| `features/pickled_core_mine_all.feature` | fail | 13 | no |
| `features/pickled_core_mine_code.feature` | fail | 14 | no |
| `features/pickled_core_mine_evaluate.feature` | fail | 13 | no |
| `features/pickled_core_mine_features.feature` | fail | 13 | no |
| `features/pickled_core_mine_inventory.feature` | fail | 10 | no |
| `features/pickled_core_mine_report.feature` | fail | 10 | no |
| `features/pickled_core_mine_stories.feature` | fail | 15 | no |
| `features/pickled_core_mine_tag.feature` | fail | 10 | no |
| `features/pickled_data_apply.feature` | fail | 19 | no |
| `features/pickled_data_check_drift.feature` | fail | 7 | no |
| `features/pickled_data_datacontractgate.feature` | fail | 14 | no |
| `features/pickled_data_draft.feature` | fail | 20 | no |
| `features/pickled_data_mcp.feature` | fail | 5 | no |
| `features/pickled_data_migrationdriftgate.feature` | fail | 18 | no |
| `features/pickled_data_parse.feature` | fail | 9 | no |
| `features/pickled_data_run_all.feature` | fail | 18 | no |
| `features/pickled_diff_draft_corpus.feature` | fail | 8 | no |
| `features/pickled_diff_mcp.feature` | fail | 3 | no |
| `features/pickled_diff_run_all.feature` | fail | 17 | no |
| `features/pickled_diff_verify.feature` | fail | 22 | no |
| `features/pickled_iac_diff.feature` | fail | 22 | no |
| `features/pickled_iac_draft.feature` | warn | 15 | no |
| `features/pickled_iac_iacambiguitygate.feature` | error | 0 | yes |
| `features/pickled_iac_mcp.feature` | fail | 6 | no |
| `features/pickled_iac_plan_cmd.feature` | fail | 8 | no |
| `features/pickled_iac_plandiffgate.feature` | fail | 28 | no |
| `features/pickled_iac_run_all.feature` | fail | 14 | no |
| `features/pickled_iac_scan.feature` | fail | 12 | no |
| `features/pickled_iac_securitybaselinegate.feature` | fail | 20 | no |
| `features/pickled_iac_validate.feature` | fail | 6 | no |
| `features/pickled_rules_check.feature` | fail | 25 | no |
| `features/pickled_rules_coverage_gate.feature` | fail | 14 | no |
| `features/pickled_rules_coverage_gate_features.feature` | fail | 12 | no |
| `features/pickled_rules_draft.feature` | fail | 13 | no |
| `features/pickled_rules_list_rules.feature` | fail | 8 | no |
| `features/pickled_rules_mcp.feature` | fail | 3 | no |
| `features/pickled_rules_run_all.feature` | fail | 19 | no |
| `features/pickled_schema_check.feature` | fail | 16 | no |
| `features/pickled_schema_draft.feature` | fail | 19 | no |
| `features/pickled_schema_mcp.feature` | fail | 2 | no |
| `features/pickled_schema_parse.feature` | error | 0 | yes |
| `features/pickled_schema_run_all.feature` | fail | 25 | no |
| `features/pickled_schema_schemaambiguitygate.feature` | warn | 17 | no |
| `features/pickled_schema_schemacoveragegate.feature` | fail | 23 | no |
| `features/pickled_schema_validate.feature` | fail | 18 | no |
| `features/rules_check_ruleset_coverage.feature` | fail | 9 | no |
| `features/rules_draft_ruleset_from_brief.feature` | fail | 12 | no |
| `features/rules_list_rules.feature` | fail | 10 | no |
| `features/schema_check_schema_coverage.feature` | fail | 7 | no |
| `features/schema_draft_openapi_endpoint.feature` | fail | 12 | no |
| `features/schema_validate_openapi_spec.feature` | fail | 5 | no |

## Suggested next moves

- Add a story/feature covering strict rules: gherkin-then-asserts-observable-outcome
- Re-draft `bdd_draft_feature_from_story` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `bdd_validate_feature_ambiguity` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `data_apply_sql_to_sandbox` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `data_check_migration_drift` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `data_draft_sql_migration_from_intent` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `data_parse_sql_migration` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `diff_draft_corpus_from_examples` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `diff_verify_against_oracle` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `iac_diff_terraform_plans` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `iac_draft_terraform_module` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `iac_explain_plan_diff` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `iac_suggest_security_remediation` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `iac_validate_terraform_dir` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_bdd_ambiguity` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_bdd_check` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_bdd_draft` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_bdd_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_bdd_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_check_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_code` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_evaluate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_features` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_inventory` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_report` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_stories` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_core_mine_tag` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_apply` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_check_drift` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_datacontractgate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_draft` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_migrationdriftgate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_parse` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_data_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_diff_draft_corpus` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_diff_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_diff_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_diff_verify` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_diff` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_plan_cmd` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_plandiffgate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_scan` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_securitybaselinegate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_iac_validate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_check` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_coverage_gate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_coverage_gate_features` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_draft` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_list_rules` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_rules_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_check` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_draft` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_mcp` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_run_all` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_schemacoveragegate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `pickled_schema_validate` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `rules_check_ruleset_coverage` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `rules_draft_ruleset_from_brief` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `rules_list_rules` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `schema_check_schema_coverage` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `schema_draft_openapi_endpoint` with tighter scope; see evaluation/ambiguity.json findings.
- Re-draft `schema_validate_openapi_spec` with tighter scope; see evaluation/ambiguity.json findings.
