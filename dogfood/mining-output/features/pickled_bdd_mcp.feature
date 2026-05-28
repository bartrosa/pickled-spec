Feature: MCP Command Group
  As a CLI user
  I want the mcp command to serve as a parent group for MCP server operations
  So that I can organize and access MCP-related subcommands

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer invokes mcp command directly
    When the mcp function is called directly
    Then it completes without raising exceptions
    And it returns None

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer invokes mcp command with no side effects
    Given no prior state exists
    When the mcp function is called directly
    Then no console output is produced
    And no global state is modified
    And no file system operations are performed
    And no network calls are made

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer checks mcp function signature
    When the mcp function signature is inspected
    Then it accepts zero parameters
