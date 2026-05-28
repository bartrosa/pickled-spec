Feature: Mine evaluate command checks coverage and ambiguity quality gates

  Background:
    Given a target codebase exists
    And mining stages 1-5 have completed successfully
    And mined surfaces exist in the output directory

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Engineer evaluates surfaces when all gates pass
    Given all configured coverage gates are satisfied
    And all configured ambiguity gates are satisfied
    When the engineer runs mine evaluate against the target
    Then the command exits with status 0
    And gate results are written to the output directory in structured format

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Engineer evaluates surfaces when any gate fails
    Given at least one configured gate is not satisfied
    When the engineer runs mine evaluate against the target
    Then the command exits with a non-zero status
    And gate results are written to the output directory in structured format

  @best-practices:llm-drafter-temperature-zero
  Scenario: CI pipeline attempts evaluation without prior mining stages
    Given mining stages 1-5 have not been run
    When the pipeline runs mine evaluate against the target
    Then the command fails or reports missing prerequisite data
    And the command exits with a non-zero status

  @data-domain:migration-drift-gate
  Scenario: Engineer evaluates with custom output directory
    Given mined artifacts exist in a custom directory
    When the engineer runs mine evaluate with the output_dir argument
    Then the command reads artifacts from the specified directory
    And evaluation results are written to the specified directory

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Engineer evaluates with verbose logging enabled
    When the engineer runs mine evaluate with the verbose flag
    Then additional diagnostic output is produced to stderr during evaluation
    And the command completes evaluation normally

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Engineer evaluates filtered surfaces
    Given surfaces exist for packages "<package_a>" and "<package_b>"
    When the engineer runs mine evaluate with surfaces filter "<filter>"
    Then gate evaluation is restricted to surfaces matching "<filter>"
    And non-matching surfaces are excluded from evaluation

    Examples:
      | package_a | package_b | filter    |
      | api.auth  | api.data  | api.auth  |
      | core.util | core.main | core      |
      | service.a | service.b | service.a |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Engineer evaluates coverage gate
    Given surfaces exist with varying documentation coverage
    And a coverage gate threshold is configured
    When the engineer runs mine evaluate against the target
    Then the coverage gate measures the percentage or count of surfaces meeting thresholds
    And the gate passes or fails based on the configured threshold

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Engineer evaluates ambiguity gate
    Given surfaces with potentially conflicting definitions exist
    And an ambiguity gate is configured
    When the engineer runs mine evaluate against the target
    Then the ambiguity gate detects conflicting or overlapping surface definitions
    And the gate passes or fails based on detected ambiguities

  @pickled-internal:core-llm-cache-default-on
  Scenario: Engineer evaluates surfaces multiple times
    Given mining and evaluation have been performed once
    And gate results have been recorded
    When the engineer runs mine evaluate again with identical inputs
    Then the gate results are identical to the previous evaluation
    And the command produces the same exit status

  # TODO: Clarify behavior when ruleset_dir is specified
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Engineer evaluates with custom ruleset directory
    Given a custom ruleset directory exists
    When the engineer runs mine evaluate with the ruleset_dir argument
    Then gate behavior is configured from the specified ruleset directory

  # TODO: Clarify behavior when ruleset_config is specified
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Engineer evaluates with custom ruleset configuration
    Given a custom ruleset configuration is provided
    When the engineer runs mine evaluate with the ruleset_config argument
    Then gate behavior is configured according to the specified ruleset configuration
