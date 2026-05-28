Feature: MCP CLI Command Entry Point
  As a CLI user
  I want to invoke the mcp command
  So that I can access MCP server functionality through the command group

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User invokes mcp command without arguments
    When the mcp command is invoked with no arguments
    Then it completes without raising exceptions
    And it returns None

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User attempts to invoke mcp command with arguments
    When the mcp command is invoked with arguments
    Then it raises a TypeError

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User invokes mcp command and checks for side effects
    When the mcp command is invoked with no arguments
    Then no file I/O operations occur
    And no network calls are made
    And no output is written to stdout
    And no output is written to stderr

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User imports and invokes mcp as a standalone function
    When the mcp function is imported from the module
    And the function is invoked directly
    Then it executes successfully
    And it returns None

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User inspects mcp command documentation
    When the mcp function docstring is retrieved
    Then it contains the string "MCP server commands."
