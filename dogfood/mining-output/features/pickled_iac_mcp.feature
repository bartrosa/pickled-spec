Feature: MCP Command Group
  As a CLI user
  I want to access MCP server commands under a "mcp" namespace
  So that I can organize and invoke MCP-related operations

  Background:
    Given the pickled-iac CLI is available

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User invokes the mcp command group programmatically
    When the mcp command group function is called
    Then it returns None
    And no exceptions are raised

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User invokes the mcp command group with no arguments
    When the user executes the "mcp" command without subcommands
    Then the command accepts no arguments
    And the command completes immediately

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: MCP command group performs no side effects
    When the mcp command group function is called
    Then no file I/O operations are performed
    And no network operations are initiated
    And no state mutations occur

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: MCP command group organizes subcommands
    Given MCP-related subcommands exist in the system
    When the user views the mcp command group
    Then subcommands are organized under the "mcp" namespace

  # TODO: Verify Click framework behavior when invoked without subcommands (help text vs error)
  @best-practices:cli-mcp-surface-parity
  Scenario: User invokes mcp command group from CLI without subcommands
    When the user executes the "mcp" command from the command line
    Then the Click framework handles the invocation
    And appropriate feedback is displayed to the user

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: MCP command group execution is non-blocking
    When the mcp command group function is called
    Then it executes without blocking
    And it completes immediately
