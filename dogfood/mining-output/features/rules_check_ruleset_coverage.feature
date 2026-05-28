Feature: MCP tool checks Gherkin feature coverage against YAML ruleset

  Background:
    Given an MCP client needs to verify feature file coverage

  @rules-domain:coverage-union-across-features
  Scenario: Client checks feature coverage against a valid ruleset
    Given a ruleset YAML text containing coverage requirements
    And one or more Gherkin feature file text contents
    And a ruleset short name identifier
    When the client invokes the rules_check_ruleset_coverage tool with ruleset_yaml_text, feature_texts, and ruleset_short_name
    Then the tool parses the YAML ruleset definition
    And the tool parses the Gherkin feature file contents
    And the tool compares the parsed features against the ruleset requirements
    And the tool returns coverage analysis results indicating whether features meet ruleset requirements

  @rules-domain:coverage-union-across-features
  Scenario: Client attempts to pass filesystem paths instead of file contents
    Given a client attempts to provide filesystem paths rather than file contents
    When the client invokes the rules_check_ruleset_coverage tool with path strings
    Then the tool rejects the request or fails safely
    And the tool does not perform filesystem reads based on the supplied paths

  @rules-domain:coverage-union-across-features
  Scenario: Tool prevents arbitrary file read attacks
    Given a malicious client attempts to exploit parser error messages
    When the client provides input designed to trigger path-based file reads
    Then the tool does not read files from the filesystem based on user-supplied paths
    And the tool does not expose file contents through parser error messages

  @rules-domain:coverage-union-across-features
  Scenario Outline: Tool validates required parameters
    Given a client invokes the tool with <missing_parameter> omitted
    When the tool processes the request
    Then the tool fails with a parameter validation error

    Examples:
      | missing_parameter    |
      | ruleset_yaml_text    |
      | feature_texts        |
      | ruleset_short_name   |

  @rules-domain:coverage-union-across-features
  Scenario: Client checks coverage with multiple feature files
    Given a ruleset YAML text containing coverage requirements
    And multiple Gherkin feature file text contents
    And a ruleset short name identifier
    When the client invokes the rules_check_ruleset_coverage tool
    Then the tool parses all provided feature file contents
    And the tool aggregates coverage across all features
    And the tool returns combined coverage analysis results

  @rules-domain:coverage-union-across-features
  Scenario: Tool handles malformed YAML ruleset
    Given a ruleset YAML text with invalid YAML syntax
    And valid Gherkin feature file text contents
    And a ruleset short name identifier
    When the client invokes the rules_check_ruleset_coverage tool
    Then the tool returns an error indicating YAML parsing failure
    And the tool does not expose filesystem information in the error message

  @rules-domain:coverage-union-across-features
  Scenario: Tool handles malformed Gherkin feature content
    Given a valid ruleset YAML text
    And Gherkin feature file text contents with invalid syntax
    And a ruleset short name identifier
    When the client invokes the rules_check_ruleset_coverage tool
    Then the tool returns an error indicating Gherkin parsing failure
    And the tool does not expose filesystem information in the error message
