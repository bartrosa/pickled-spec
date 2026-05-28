Feature: List rules from rule set
  As a CLI user
  I want to list rule identifiers from a rule set
  So that I can reference specific rules for filtering, reporting, or configuration

  @rules-domain:unknown-tag-fails-gate
  Scenario: User lists rules from a built-in rule set
    Given a built-in rule set "standard" exists
    When the user lists rules from rule set "standard"
    Then the command outputs the rule IDs from the "standard" rule set
    And the command exits with code 0

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User lists rules from a custom YAML file
    Given a YAML rule set file exists at "custom-rules.yaml"
    When the user lists rules from rule set "custom-rules.yaml"
    Then the command outputs the rule IDs from the file "custom-rules.yaml"
    And the command exits with code 0

  @best-practices:llm-drafter-temperature-zero
  Scenario: User attempts to list rules from a non-existent built-in rule set
    Given no built-in rule set named "nonexistent" exists
    When the user lists rules from rule set "nonexistent"
    Then the command produces an error indicating the rule set was not found
    And the command exits with a non-zero code

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to list rules from a non-existent file path
    Given no file exists at "missing-rules.yaml"
    When the user lists rules from rule set "missing-rules.yaml"
    Then the command produces an error indicating the rule set was not found
    And the command exits with a non-zero code

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to list rules from an invalid YAML file
    Given an invalid YAML file exists at "invalid-rules.yaml"
    When the user lists rules from rule set "invalid-rules.yaml"
    Then the command produces an error indicating the rule set is invalid
    And the command exits with a non-zero code

  @rules-domain:unknown-tag-fails-gate
  Scenario Outline: User lists rules from different built-in rule sets
    Given a built-in rule set "<ruleset_name>" exists
    When the user lists rules from rule set "<ruleset_name>"
    Then the command outputs the rule IDs from the "<ruleset_name>" rule set
    And the command exits with code 0

    Examples:
      | ruleset_name |
      | standard     |
      | strict       |
      | minimal      |
