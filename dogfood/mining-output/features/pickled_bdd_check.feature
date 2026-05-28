Feature: Check feature file quality with gates
  As a developer or CI/CD pipeline
  I want to validate Gherkin feature files for quality issues
  So that I can enforce standards and catch ambiguity problems early

  Background:
    Given a feature file exists at "sample.feature"

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer checks a valid feature file with LLM available
    Given the LLM client is available
    When the check command is invoked with the feature file path
    Then the command produces JSON output to stdout
    And the JSON contains exactly four top-level keys: "gate", "verdict", "notes", "findings"
    And the "gate" value is "ambiguity"
    And the process exits with code 0

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer checks a feature file when LLM is unavailable
    Given the LLM client is unavailable
    When the check command is invoked with the feature file path
    Then the JSON contains exactly four top-level keys: "gate", "verdict", "notes", "findings"
    And the "gate" value is "ambiguity"
    And the "verdict" value is "PASS"
    And the "notes" value indicates the gate was skipped due to unavailable LLM
    And the "findings" array is empty
    And the process exits with code 0

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario Outline: Developer receives appropriate exit codes based on verdict
    Given the LLM client is available
    And the ambiguity gate will return verdict "<verdict>"
    When the check command is invoked with the feature file path
    Then the process exits with code <exit_code>

    Examples:
      | verdict | exit_code |
      | PASS    | 0         |
      | WARN    | 1         |
      | FAIL    | 2         |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer encounters LLM client configuration error
    Given the LLM client factory is configured with invalid settings
    When the check command is invoked with the feature file path
    Then a ClickException is raised with the configuration error message

  # TODO: Clarify expected behavior when feature_file path does not exist or is invalid
  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer provides gate parameter
    Given the LLM client is available
    When the check command is invoked with gate parameter "<gate_name>"
    Then the ambiguity gate executes regardless of the parameter value
    And the "gate" value is "ambiguity"

    Examples:
      | gate_name  |
      | ambiguity  |
      | some-other |
      | invalid    |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer verifies JSON output format
    Given the LLM client is available
    And the ambiguity gate returns findings with Unicode characters
    When the check command is invoked with the feature file path
    Then the JSON output uses 2-space indentation
    And the JSON output preserves Unicode characters without escaping

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer receives findings filtered by type
    Given the LLM client is available
    And the ambiguity gate returns mixed finding types
    When the check command is invoked with the feature file path
    Then the "findings" array contains only AmbiguityFinding instances
    And each finding contains "scenario", "alternatives", and "suggested_fix" keys
    And the "alternatives" value is a list

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer verifies finding structure
    Given the LLM client is available
    And the ambiguity gate returns an AmbiguityFinding
    When the check command is invoked with the feature file path
    Then each finding object has a "scenario" key with the target name
    And each finding object has an "alternatives" key with a list value
    And each finding object has a "suggested_fix" key
