Feature: Draft ruleset from brief description
  As an agent or client using pickled-rules
  I want to generate a complete ruleset from a brief text description
  So that I can quickly create draft rulesets with appropriate metadata

  Background:
    Given a multi-ruleset workspace environment

  @best-practices:agent-path-first-class
  Scenario: Agent drafts ruleset with all required parameters
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Require security review for API changes  |
      | ruleset_short_name | api_security                             |
      | source_id          | SEC-2024-001                             |
      | applies_to         | api_endpoints                            |
      | active_from        | 2024-01-01                               |
    Then the tool responds without parameter validation errors
    And the response represents a ruleset structure

  @best-practices:agent-path-first-class
  Scenario: Agent drafts ruleset incorporating short name
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Validate input formats                   |
      | ruleset_short_name | input_validation                         |
      | source_id          | DEV-100                                  |
      | applies_to         | user_inputs                              |
      | active_from        | 2024-02-01                               |
    Then the generated ruleset incorporates "input_validation" as its short name

  @best-practices:agent-path-first-class
  Scenario: Agent drafts ruleset incorporating source identifier
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Enforce code style standards             |
      | ruleset_short_name | code_style                               |
      | source_id          | STYLE-500                                |
      | applies_to         | source_code                              |
      | active_from        | 2024-03-01                               |
    Then the generated ruleset incorporates "STYLE-500" as its source identifier

  @rules-domain:coverage-union-across-features
  Scenario: Agent drafts ruleset incorporating scope
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Check documentation completeness         |
      | ruleset_short_name | doc_checks                               |
      | source_id          | DOC-200                                  |
      | applies_to         | markdown_files                           |
      | active_from        | 2024-04-01                               |
    Then the generated ruleset incorporates "markdown_files" as its scope

  @best-practices:agent-path-first-class
  Scenario: Agent drafts ruleset incorporating temporal constraint
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Restrict deprecated API usage            |
      | ruleset_short_name | deprecation_policy                       |
      | source_id          | API-300                                  |
      | applies_to         | legacy_endpoints                         |
      | active_from        | 2024-06-15                               |
    Then the generated ruleset incorporates "2024-06-15" as its activation date

  @best-practices:agent-path-first-class
  Scenario: Agent drafts ruleset with content relating to brief
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                          |
      | brief_text         | All database queries must use parameterization |
      | ruleset_short_name | sql_safety                                     |
      | source_id          | DB-400                                         |
      | applies_to         | database_layer                                 |
      | active_from        | 2024-05-01                                     |
    Then the generated ruleset content relates to parameterized database queries

  @best-practices:agent-path-first-class
  Scenario Outline: Agent invokes tool with missing required parameter
    When the agent invokes rules_draft_ruleset_from_brief with <missing_parameter> omitted
    Then the tool returns an appropriate error

    Examples:
      | missing_parameter  |
      | brief_text         |
      | ruleset_short_name |
      | source_id          |
      | applies_to         |
      | active_from        |

  @best-practices:agent-path-first-class
  Scenario: Agent drafts multiple rulesets in workspace
    Given an existing ruleset "data_validation" is already in the workspace
    When the agent invokes rules_draft_ruleset_from_brief with:
      | parameter          | value                                    |
      | brief_text         | Audit trail for all mutations            |
      | ruleset_short_name | audit_logging                            |
      | source_id          | AUDIT-600                                |
      | applies_to         | data_mutations                           |
      | active_from        | 2024-07-01                               |
    Then the new ruleset is created within the multi-ruleset workspace context
    And the existing ruleset "data_validation" remains unaffected
