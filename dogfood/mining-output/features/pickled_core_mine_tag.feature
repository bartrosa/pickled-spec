Feature: Mine tag command
  As a developer or automation pipeline
  I want to tag scenarios in generated feature files
  So that I can categorize and filter test cases for downstream processing

  Background:
    Given the pickled-core mining pipeline has completed prior stages
    And feature files have been generated

  @bdd-domain:drafter-no-auto-tags
  Scenario: Developer tags scenarios with valid target
    Given a valid target is specified
    When the mine tag command is executed
    Then scenarios in the generated feature files are tagged
    And the tagged features are written to the mining output directory

  @best-practices:agent-path-first-class
  Scenario: Developer specifies custom output directory
    Given a valid target is specified
    And an output directory path is provided via "--output-dir"
    When the mine tag command is executed
    Then the tagged features are written to the specified output directory

  @bdd-domain:drafter-no-auto-tags
  Scenario Outline: Developer controls interactive mode with quick flag
    Given a valid target is specified
    And the "--quick" flag is set to <quick_value>
    When the mine tag command is executed
    Then the command runs in <mode> mode
    And <interaction_behavior>

    Examples:
      | quick_value | mode        | interaction_behavior                  |
      | true        | quick       | no interactive prompts are displayed  |
      | false       | interactive | interactive prompts are enabled       |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer enables verbose logging
    Given a valid target is specified
    And the "--verbose" flag is enabled
    When the mine tag command is executed
    Then extra logging output is written to stderr
    And scenarios are tagged successfully

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer filters surfaces by package name or surface ID
    Given a valid target is specified
    And the "--surfaces" parameter contains comma-separated filter substrings
    When the mine tag command is executed
    Then only surfaces matching the package name or surface ID substrings are processed
    And matching surfaces have their scenarios tagged

  @bdd-domain:drafter-no-auto-tags
  Scenario: Developer configures ruleset directory
    Given a valid target is specified
    And a ruleset directory path is provided via "--ruleset-dir"
    When the mine tag command is executed
    Then ruleset definitions are loaded from the specified directory
    And scenarios are tagged according to the rulesets

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer configures ruleset configuration per ADR 0004
    Given a valid target is specified
    And a ruleset configuration is provided via "--ruleset-config"
    When the mine tag command is executed
    Then the multi-ruleset workspace configuration is applied per ADR 0004
    And scenarios are tagged according to the configured rulesets

  @bdd-domain:drafter-no-auto-tags
  Scenario: Developer omits required target parameter
    Given the target parameter is not provided
    When the mine tag command is executed
    Then the command fails with an error
    And an appropriate error message indicates the target parameter is required

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Command operates as stage 5 in mining pipeline
    Given stages 1 through 4 of the mining pipeline have completed
    And feature files exist from prior stages
    When the mine tag command is executed as stage 5
    Then scenarios are tagged in the existing feature files
    And the tagged output is ready for downstream processing
