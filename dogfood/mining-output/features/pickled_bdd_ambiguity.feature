Feature: Ambiguity CLI command
  As a developer using pickled-bdd
  I want to run ambiguity analysis on a Gherkin feature file via a CLI shortcut
  So that I can quickly check for ambiguous scenarios without verbose syntax

  Background:
    Given a Gherkin feature file exists at a known path

  @best-practices:agent-path-first-class
  Scenario: User invokes ambiguity command with required feature file argument
    When the user runs the ambiguity command with a feature file path
    Then the command accepts the feature file argument

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Command writes informational message to stderr
    When the user runs the ambiguity command with a feature file path
    Then stderr contains the message "(equivalent to: pickled-bdd check --gate ambiguity)"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Command fails when LLM configuration is invalid
    Given the LLM configuration environment is invalid
    When the user runs the ambiguity command with a feature file path
    Then a ClickException is raised with the configuration error message

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Command passes when LLM is unavailable
    Given the LLM client is unavailable
    When the user runs the ambiguity command with a feature file path
    Then the JSON output contains verdict "PASS"
    And the JSON output contains notes "LLM unavailable; ambiguity gate skipped"
    And the command exits with code 0

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Command outputs valid JSON structure to stdout
    Given the LLM client is available
    When the user runs the ambiguity command with a feature file path
    Then the JSON output is written to stdout
    And the JSON output contains key "gate"
    And the JSON output contains key "verdict"
    And the JSON output contains key "notes"
    And the JSON output contains key "findings"

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Gate field always contains ambiguity value
    Given the LLM client is available
    When the user runs the ambiguity command with a feature file path
    Then the JSON output field "gate" has value "ambiguity"

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario Outline: Verdict field contains valid enum string value
    Given the LLM client is available
    And the ambiguity gate returns a <verdict> verdict
    When the user runs the ambiguity command with a feature file path
    Then the JSON output field "verdict" has value "<verdict>"

    Examples:
      | verdict |
      | PASS    |
      | WARN    |
      | FAIL    |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Findings array contains properly structured ambiguity findings
    Given the LLM client is available
    And the ambiguity gate detects ambiguous scenarios
    When the user runs the ambiguity command with a feature file path
    Then each finding in the JSON output contains key "scenario"
    And each finding in the JSON output contains key "alternatives"
    And each finding in the JSON output contains key "suggested_fix"

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario Outline: Command exits with code based on verdict
    Given the LLM client is available
    And the ambiguity gate returns a <verdict> verdict
    When the user runs the ambiguity command with a feature file path
    Then the command exits with code <exit_code>

    Examples:
      | verdict | exit_code |
      | PASS    | 0         |
      | WARN    | 1         |
      | FAIL    | 2         |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: JSON output is formatted with proper indentation and encoding
    Given the LLM client is available
    When the user runs the ambiguity command with a feature file path
    Then the JSON output uses 2-space indentation
    And the JSON output preserves non-ASCII characters
