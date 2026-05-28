Feature: Pipeline operator generates mining report
  As a pipeline operator
  I want to generate a consolidated mining report from pipeline outputs
  So that I can review, hand off, or archive the analysis results

  Background:
    Given the pickled pipeline has completed stages 1 through 6
    And mining artifacts exist in the output directory

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator generates report with valid target
    When the operator runs "pickled-core mine report <target>"
    Then the command exits successfully
    And a file named "mining-report.md" is created
    And the report contains consolidated information from prior pipeline stages

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator generates report from custom output directory
    Given mining artifacts are located in a custom directory
    When the operator runs "pickled-core mine report <target> --output_dir <custom_path>"
    Then the command reads mining artifacts from the custom directory
    And the command exits successfully
    And a file named "mining-report.md" is created

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator generates report with verbose logging
    When the operator runs "pickled-core mine report <target> --verbose"
    Then the command exits successfully
    And additional logging messages are emitted to stderr
    And a file named "mining-report.md" is created

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator filters report by surface criteria
    Given multiple surfaces exist across different packages
    When the operator runs "pickled-core mine report <target> --surfaces <filter>"
    Then the command exits successfully
    And the generated report includes only surfaces matching the filter criteria
    And surfaces not matching the filter are excluded from the report

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator runs report in interactive mode
    When the operator runs "pickled-core mine report <target> --quick=false"
    Then the command prompts for interactive input
    And the command exits successfully after input is provided
    And a file named "mining-report.md" is created

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Operator omits required target argument
    When the operator runs "pickled-core mine report" without a target argument
    Then the command fails with an appropriate error message
    And no report file is created

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Operator combines multiple options
    When the operator runs "pickled-core mine report <target> <options>"
    Then the command exits successfully
    And the behavior reflects all specified options

    Examples:
      | options                                    |
      | --verbose --output_dir custom              |
      | --surfaces filter1,filter2 --verbose       |
      | --quick=false --verbose                    |
      | --output_dir custom --surfaces filter      |
