Feature: Mine code from a target codebase
  As a developer or automation system
  I want to extract source code context from software projects
  So that I can document, analyze, or use the code for AI-assisted workflows

  @best-practices:llm-drafter-temperature-zero
  Scenario: Developer mines code without providing required target argument
    When a developer invokes the mine code command without a target
    Then the command fails with a non-zero exit code
    And an error message indicates the target argument is required

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Developer mines code to default output location
    Given a valid target codebase exists
    When a developer invokes the mine code command with the target
    Then the command exits with code 0
    And mining results are written to the default output directory
    And structured output files contain surface metadata
    And structured output files contain source code
    And structured output files contain call graph information

  @best-practices:agent-path-first-class
  Scenario: Developer mines code to specified output directory
    Given a valid target codebase exists
    And an output directory path is specified
    When a developer invokes the mine code command with the target and output_dir
    Then the command exits with code 0
    And mining results are written to the specified output directory

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer mines code with verbose logging enabled
    Given a valid target codebase exists
    When a developer invokes the mine code command with the target and verbose flag
    Then the command exits with code 0
    And additional diagnostic information is written to stderr during mining

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Developer filters surfaces by package or surface-id substring
    Given a valid target codebase exists with multiple surfaces
    And the surfaces parameter is set to "<filter>"
    When a developer invokes the mine code command with the target and surfaces filter
    Then the command exits with code 0
    And only surfaces matching "<filter>" are included in the output

    Examples:
      | filter              |
      | package_name        |
      | surface_id_fragment |

  @oss-hygiene:no-secrets-in-repo
  Scenario: Developer controls source code context depth
    Given a valid target codebase exists
    And the depth parameter is set to a specific value
    When a developer invokes the mine code command with the target and depth
    Then the command exits with code 0
    And the collected source code context matches the specified depth level

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer determines which intra-project callees to follow
    Given a valid target codebase exists with intra-project function calls
    And the callee_scope parameter is set to a specific scope
    When a developer invokes the mine code command with the target and callee_scope
    Then the command exits with code 0
    And only callees within the specified scope are followed during analysis

  Scenario: Developer limits call graph traversal depth with max_hops
    Given a valid target codebase exists with nested function calls
    And the max_hops parameter is set to a specific value
    When a developer invokes the mine code command with the target and max_hops
    Then the command exits with code 0
    And callee expansion is capped at the specified number of hops

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Developer limits number of callee units per surface
    Given a valid target codebase exists with multiple callees per surface
    And the max_callees parameter is set to a specific limit
    When a developer invokes the mine code command with the target and max_callees
    Then the command exits with code 0
    And the number of collected callee units per surface does not exceed the limit

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Developer limits total source lines per surface
    Given a valid target codebase exists
    And the max_code_lines parameter is set to a specific limit
    When a developer invokes the mine code command with the target and max_code_lines
    Then the command exits with code 0
    And the total source lines collected per surface does not exceed the limit

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer detects circular dependencies in call graph
    Given a valid target codebase exists with circular dependencies
    And the detect_cycles flag is enabled
    When a developer invokes the mine code command with the target and detect_cycles
    Then the command exits with code 0
    And a code-context/_cycles.json file is written to the output directory
    And the cycles file contains detected circular dependencies from call graph edges

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer mines code without cycle detection
    Given a valid target codebase exists
    When a developer invokes the mine code command with the target
    Then the command exits with code 0
    And no code-context/_cycles.json file is written

  @best-practices:agent-path-first-class
  Scenario: Automation system mines code and encounters an error
    Given an invalid target codebase path
    When an automation system invokes the mine code command with the invalid target
    Then the command exits with a non-zero exit code
