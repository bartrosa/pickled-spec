Feature: Differential testing gate entry point
  As a pickled gate runner
  I want to execute differential testing comparing candidate and oracle implementations
  So that I can verify behavioral equivalence across a test corpus

  Background:
    Given a working directory

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Configuration file is missing
    Given no "pickled.diff.yaml" configuration file exists
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.config"
    And the GateResult has verdict WARN
    And the GateResult notes mention the missing configuration file

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Configuration file has non-string corpus value
    Given a "pickled.diff.yaml" configuration file exists
    And the corpus key is not a string
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.config"
    And the GateResult has verdict FAIL

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Configuration file has invalid command format
    Given a "pickled.diff.yaml" configuration file exists
    And the <command_key> is not a list
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.config"
    And the GateResult has verdict FAIL

    Examples:
      | command_key       |
      | oracle_command    |
      | candidate_command |

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Configuration file is valid
    Given a "pickled.diff.yaml" configuration file exists
    And the oracle_command is a valid list
    And the candidate_command is a valid list
    And the corpus is a valid string path
    And a corpus file exists at the specified path
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.differential_oracle"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Python executable substitution in commands
    Given a "pickled.diff.yaml" configuration file exists
    And the <command_key> starts with "<python_token>"
    And the <command_key> has more than one element
    And the corpus is a valid string path
    And a corpus file exists at the specified path
    When the run_all gate is invoked
    Then the subprocess runner for <runner_name> uses sys.executable as the first argument

    Examples:
      | command_key       | python_token | runner_name |
      | oracle_command    | python       | oracle      |
      | oracle_command    | python3      | oracle      |
      | candidate_command | python       | candidate   |
      | candidate_command | python3      | candidate   |

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Python executable substitution requires multiple command elements
    Given a "pickled.diff.yaml" configuration file exists
    And the oracle_command is ["python"]
    And the corpus is a valid string path
    And a corpus file exists at the specified path
    When the run_all gate is invoked
    Then the subprocess runner for oracle does not substitute sys.executable

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Configuration defaults for optional fields
    Given a "pickled.diff.yaml" configuration file exists
    And the oracle_command is a valid list
    And the candidate_command is a valid list
    And the corpus is a valid string path
    And timeout_seconds is not specified
    And comparator is not specified
    And a corpus file exists at the specified path
    When the run_all gate is invoked
    Then the timeout is set to 30 seconds
    And the comparator is set to "exact"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: FileNotFoundError during configuration loading results in FAIL
    Given configuration loading raises FileNotFoundError
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.config"
    And the GateResult has verdict FAIL
    And the GateResult notes contain the exception message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Configuration parsing errors result in FAIL
    Given a "pickled.diff.yaml" configuration file exists
    And configuration parsing raises <exception_type>
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has gate_name "diff.config"
    And the GateResult has verdict FAIL
    And the GateResult notes contain the exception message

    Examples:
      | exception_type       |
      | ValueError           |
      | json.JSONDecodeError |
      | TypeError            |

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: JSONDecodeError during corpus loading results in FAIL
    Given a "pickled.diff.yaml" configuration file exists
    And the configuration is valid
    And corpus loading raises json.JSONDecodeError
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
    And the GateResult has verdict FAIL
    And the GateResult notes contain the exception message

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Return value always contains exactly one GateResult
    Given any valid or invalid configuration state
    When the run_all gate is invoked
    Then a list with exactly one GateResult is returned
