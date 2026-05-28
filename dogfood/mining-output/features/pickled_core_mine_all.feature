Feature: Mine all command orchestrates the complete mining pipeline

  As a developer or QA engineer
  I want to run a single command that executes all mining stages
  So that I can extract, document, tag, evaluate, and report on software surfaces end-to-end

  Background:
    Given a valid target codebase exists

  @best-practices:agent-path-first-class
  Scenario: User runs mine all with a valid target
    When the user invokes mine all with the target codebase
    Then the inventory stage runs first
    And the code stage runs after inventory
    And the stories stage runs after code
    And the features stage runs after stories
    And the tag stage runs after features
    And the evaluate stage runs after tag
    And the report stage runs after evaluate
    And the command exits with status 0

  @best-practices:llm-drafter-temperature-zero
  Scenario: User omits the required target parameter
    When the user invokes mine all without specifying a target
    Then the command raises an error indicating target is required
    And the command exits with a non-zero status

  @best-practices:agent-path-first-class
  Scenario: User specifies a custom output directory
    When the user invokes mine all with target and output_dir set to "custom/output/path"
    Then all mining artifacts are written to "custom/output/path"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User requests verbose logging
    When the user invokes mine all with target and the verbose flag enabled
    Then detailed logging output is written to stderr
    And the command completes all seven stages

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User filters surfaces by package or surface-id substring
    When the user invokes mine all with target and surfaces filter set to "auth"
    Then only surfaces whose package name or surface-id contains "auth" are processed
    And surfaces not matching the filter are excluded

  @pickled-internal:core-llm-cache-default-on
  Scenario: User limits concurrent LLM calls
    When the user invokes mine all with target and max_parallel set to 3
    Then the stories stage uses at most 3 concurrent LLM calls
    And the features stage uses at most 3 concurrent LLM calls

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User specifies custom ruleset configuration
    When the user invokes mine all with target and ruleset_dir set to "custom/rulesets"
    And ruleset_config is set to "custom_rules.yaml"
    Then the tag stage applies rulesets from "custom/rulesets" using "custom_rules.yaml"

  @rules-domain:coverage-union-across-features
  Scenario Outline: User controls overwrite behavior for stories and features
    When the user invokes mine all with target and <flag> enabled
    Then existing <artifact_type> files are replaced during the <stage> stage

    Examples:
      | flag                | artifact_type | stage    |
      | overwrite_stories   | story         | stories  |
      | overwrite_features  | feature       | features |

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: User adjusts code-collection parameters
    When the user invokes mine all with target and depth set to 2
    And callee_scope is set to "same_package"
    And max_hops is set to 3
    And max_callees is set to 50
    And max_code_lines is set to 2000
    Then the code stage collects source context per surface using those constraints
    And the volume and scope of extracted code reflects the specified limits

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User enables cycle detection in the call graph
    When the user invokes mine all with target and detect_cycles flag enabled
    And the code stage detects call-graph cycles
    Then a "code-context/_cycles.json" file is written

  @best-practices:llm-drafter-temperature-zero
  Scenario: A pipeline stage fails during execution
    Given the code stage will encounter a fatal error
    When the user invokes mine all with target
    Then the command stops execution at the code stage
    And subsequent stages do not run
    And the command exits with a non-zero status

  @data-domain:migration-drift-gate
  Scenario: User runs in non-quick mode with interactive prompts
    Given quick mode is disabled
    When the user invokes mine all with target
    Then the command prompts the user for confirmation at interactive decision points
    And the command proceeds based on user responses
