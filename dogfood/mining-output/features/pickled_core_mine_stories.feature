Feature: Mine stories from inventory
  As a developer or CI pipeline
  I want to generate human-readable story files from mined surface metadata
  So that I can document behavior and prepare for feature-file generation

  Background:
    Given an inventory file exists at "target/inventory.json"

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Developer generates stories from inventory
    When the developer runs mine stories for the target directory
    Then story files are generated in the output directory structure
    And each story corresponds to a surface from the inventory

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer filters surfaces by package name
    Given the inventory contains surfaces from multiple packages
    When the developer runs mine stories with surfaces filter "pickled-core"
    Then only story files for surfaces in package "pickled-core" are generated

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer filters surfaces by surface-id substring
    Given the inventory contains multiple surfaces
    When the developer runs mine stories with surfaces filter "mine_stories"
    Then only story files matching the surface-id substring are generated

  @data-domain:migration-drift-gate
  Scenario: Developer runs in quick mode by default
    When the developer runs mine stories without specifying quick mode
    Then the command runs in batch mode without interactive prompts

  @data-domain:migration-drift-gate
  Scenario: Developer runs in interactive mode
    When the developer runs mine stories with quick mode disabled
    Then the command prompts interactively for user input

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer limits concurrent LLM operations
    When the developer runs mine stories with max_parallel set to 3
    Then no more than 3 LLM calls execute concurrently

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Developer overwrites existing story files
    Given story files already exist in the output directory
    When the developer runs mine stories with overwrite_stories enabled
    Then existing story files are replaced with newly generated content

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Developer preserves existing story files
    Given story files already exist in the output directory
    When the developer runs mine stories with overwrite_stories disabled
    Then existing story files are not replaced

  @best-practices:agent-path-first-class
  Scenario: Developer specifies custom code-context directory
    Given code-context files exist at "custom/path/code-context"
    When the developer runs mine stories with code_context_dir set to "custom/path/code-context"
    Then implementation details from the custom directory are integrated into stories

  @data-domain:migration-drift-gate
  Scenario: Developer uses default code-context directory
    Given code-context files exist at "output/code-context"
    When the developer runs mine stories without specifying code_context_dir
    Then implementation details from "output/code-context" are integrated into stories

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Developer generates stories without code-context
    Given no code-context directory exists
    When the developer runs mine stories
    Then story files are generated without implementation details

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer enables verbose logging
    When the developer runs mine stories with verbose enabled
    Then extra diagnostic output is emitted to stderr

  @best-practices:cli-mcp-surface-parity
  Scenario: Developer generates code-aware stories for drift detection
    Given code-context files exist for surfaces in the inventory
    When the developer runs mine stories
    Then generated stories integrate code-context details
    And stories support docstring drift detection per ADR 0007

  @best-practices:agent-path-first-class
  Scenario Outline: Developer specifies output directory
    When the developer runs mine stories with output_dir set to "<output_path>"
    Then story files are generated in "<output_path>"

    Examples:
      | output_path      |
      | custom/output    |
      | mining-results   |
