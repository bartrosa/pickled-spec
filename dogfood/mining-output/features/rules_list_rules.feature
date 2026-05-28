Feature: List rules from YAML rule set
  As a developer or CI/CD pipeline
  I want to extract rule definitions from YAML rule set content
  So that I can inspect and validate rule structure without executing them

  @rules-domain:unknown-tag-fails-gate
  Scenario: Developer lists rules from valid YAML rule set
    Given a valid YAML rule set containing 3 rules
    When the ruleset_yaml_text is provided to the list rules tool
    Then the tool returns a collection of 3 rule summaries
    And each rule summary includes the rule name or identifier

  @rules-domain:unknown-tag-fails-gate
  Scenario: Developer lists rules preserving original order
    Given a valid YAML rule set with rules in a specific order
    When the ruleset_yaml_text is provided to the list rules tool
    Then the returned rule summaries maintain the original YAML order

  @rules-domain:unknown-tag-fails-gate
  Scenario: Developer handles YAML with no rules
    Given a valid YAML document containing no rule definitions
    When the ruleset_yaml_text is provided to the list rules tool
    Then the tool returns an empty collection

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer handles invalid YAML input
    Given malformed YAML content that cannot be parsed
    When the ruleset_yaml_text is provided to the list rules tool
    Then the tool handles the error gracefully without crashing
    And the tool returns an error indicator or empty result

  @rules-domain:unknown-tag-fails-gate
  Scenario: Developer receives MCP-compatible output
    Given a valid YAML rule set containing rules
    When the ruleset_yaml_text is provided to the list rules tool
    Then the tool returns results in MCP-compatible format

  # TODO: Confirm exact structure of rule summaries returned (beyond name/identifier)
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer inspects rule summary content
    Given a valid YAML rule set with a rule containing metadata
    When the ruleset_yaml_text is provided to the list rules tool
    Then each rule summary includes at minimum the rule identifier
    And the summaries conform to pickled-rules package schema expectations

  @rules-domain:unknown-tag-fails-gate
  Scenario Outline: Developer lists rules from various YAML structures
    Given a YAML rule set with <rule_count> rules
    When the ruleset_yaml_text is provided to the list rules tool
    Then the tool returns a collection of <rule_count> rule summaries

    Examples:
      | rule_count |
      | 0          |
      | 1          |
      | 5          |
      | 50         |
