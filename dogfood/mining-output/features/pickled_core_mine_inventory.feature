Feature: Mine inventory from target project
  As a developer or CI pipeline
  I want to mine an inventory of specifications from a target project
  So that I can catalog discovered features and scenarios for further processing

  Background:
    Given the pickled-core mining pipeline is available
    And I have access to the filesystem

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer successfully mines inventory from valid target
    Given a valid target project exists at "examples/demo-app"
    When I run the mine inventory command with target "examples/demo-app"
    Then the command completes without error
    And an "inventory.json" file is created in the default output directory
    And the "inventory.json" file contains valid JSON
    And the inventory contains introspected elements from the target

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer mines inventory to custom output directory
    Given a valid target project exists at "examples/demo-app"
    And an output directory "custom/output" is available
    When I run the mine inventory command with target "examples/demo-app" and output_dir "custom/output"
    Then the command completes without error
    And an "inventory.json" file is created in "custom/output"
    And the "inventory.json" file contains valid JSON

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer runs mine inventory with verbose logging
    Given a valid target project exists at "examples/demo-app"
    When I run the mine inventory command with target "examples/demo-app" and verbose flag enabled
    Then the command completes without error
    And an "inventory.json" file is created
    And additional logging output is written to stderr

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer mines inventory without MCP tools
    Given a valid target project exists at "examples/demo-app"
    When I run the mine inventory command with target "examples/demo-app" and no_mcp flag enabled
    Then the command completes without error
    And an "inventory.json" file is created
    And no MCP tools list operations were performed

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer runs mine inventory in quick mode
    Given a valid target project exists at "examples/demo-app"
    When I run the mine inventory command with target "examples/demo-app" and quick flag enabled
    Then the command completes without error
    And an "inventory.json" file is created
    And no interactive prompts were displayed

  Scenario: Developer attempts to mine inventory without specifying target
    When I run the mine inventory command without a target argument
    Then the command fails with an error
    And the error message indicates the target argument is required

  @best-practices:agent-path-first-class
  Scenario: Developer attempts to mine inventory from invalid target
    Given no project exists at "nonexistent/path"
    When I run the mine inventory command with target "nonexistent/path"
    Then the command fails with an error
    And the error message indicates the target is invalid or not found

  # TODO: Specify behavior when mcp_timeout is provided and MCP operations exceed timeout
  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Developer mines inventory with different valid targets
    Given a valid target project exists at "<target_path>"
    When I run the mine inventory command with target "<target_path>"
    Then the command completes without error
    And an "inventory.json" file is created
    And the inventory contains introspected elements from the target

    Examples:
      | target_path           |
      | examples/demo-app     |
      | src/myproject         |
      | /absolute/path/proj   |
