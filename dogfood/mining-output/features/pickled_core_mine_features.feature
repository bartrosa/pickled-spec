Feature: Mine features from user stories
  As a developer using pickled-core
  I want to mine features from previously generated user stories
  So that I can create testable feature specifications in stage 4 of the mining pipeline

  Background:
    Given user stories have been generated in a previous mining stage

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer mines features with required target argument
    When the developer mines features for a target
    Then features are drafted from the user stories
    And the features are written to the default output directory

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer mines features to a specific output directory
    When the developer mines features for a target with a specified output directory
    Then features are drafted from the user stories
    And the features are written to the specified output directory

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer mines features in quick mode
    Given quick mode is enabled
    When the developer mines features for a target
    Then features are drafted without interactive prompts
    And the process uses the default quick mode behavior

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer mines features with interactive prompts
    Given quick mode is disabled
    When the developer mines features for a target
    Then features are drafted using interactive prompts

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer mines features with verbose logging
    Given verbose mode is enabled
    When the developer mines features for a target
    Then features are drafted from the user stories
    And extra logging output is written to stderr

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer filters features by surface substring
    When the developer mines features for a target with a surfaces filter
    Then only features matching the package name or surface-id substring are drafted

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer controls parallel processing
    Given quick mode is enabled
    When the developer mines features for a target with a specified max parallel value
    Then features are drafted with the specified maximum parallel LLM calls

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer overwrites existing features
    Given features already exist for the target
    And the overwrite features flag is enabled
    When the developer mines features for a target
    Then the existing features are overwritten with newly drafted features

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer runs mining as stage 4 of the pipeline
    Given the mining pipeline is at stage 4
    When the developer mines features for a target
    Then features are drafted according to ADR 0005 staged mining pipeline
    And the output reflects stage 4 processing

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario Outline: Developer mines features with different flag combinations
    Given quick mode is <quick_mode>
    And verbose mode is <verbose_mode>
    When the developer mines features for a target
    Then features are drafted with quick mode <quick_behavior>
    And logging is <logging_behavior>

    Examples:
      | quick_mode | verbose_mode | quick_behavior     | logging_behavior |
      | enabled    | enabled      | without prompts    | verbose          |
      | enabled    | disabled     | without prompts    | standard         |
      | disabled   | enabled      | with prompts       | verbose          |
      | disabled   | disabled     | with prompts       | standard         |
