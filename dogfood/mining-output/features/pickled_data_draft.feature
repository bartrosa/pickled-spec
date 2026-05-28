Feature: Draft SQL migration from natural language intent
  As a developer or automation pipeline
  I want to generate SQL migration files from natural-language descriptions
  So that I can create schema changes without manually writing DDL

  Background:
    Given the LLM client is configured via environment variable "PICKLED_DATA_LLM_FACTORY"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer reads intent from standard input
    Given the intent is provided as "-"
    And standard input contains "add user email column"
    When the draft command is invoked
    Then the LLM prompt is built with the stdin content

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer reads intent from a file
    Given the intent is provided as a file path "intent.txt"
    And the file "intent.txt" contains "add user email column"
    When the draft command is invoked
    Then the file content is read and used in the LLM prompt

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer drafts migration without current schema context
    Given the intent is "add user email column"
    And the current_schema parameter is None
    When the draft command is invoked
    Then no schema YAML file is read
    And the LLM prompt indicates "none" for schema context

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer drafts migration with current schema context
    Given the intent is "add user email column"
    And the current_schema parameter is "schema.yaml"
    And the file "schema.yaml" contains valid YAML schema definition
    When the draft command is invoked
    Then the file "schema.yaml" is read as UTF-8
    And the schema content is included in the LLM prompt

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer specifies SQL dialect for migration
    Given the intent is "add user email column"
    And the dialect is "postgres"
    When the draft command is invoked
    Then the dialect "postgres" is passed to the LLM prompt
    And the dialect "postgres" is used for sqlglot parse validation

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer writes SQL to standard output
    Given the intent is "add user email column"
    And the output parameter is None
    And the LLM generates valid SQL migration text
    When the draft command is invoked
    Then the SQL text is written to standard output

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer writes SQL to a file
    Given the intent is "add user email column"
    And the output parameter is "migration.sql"
    And the LLM generates valid SQL migration text
    When the draft command is invoked
    Then the SQL text is written to "migration.sql" as UTF-8

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer receives rationale with SQL migration
    Given the intent is "add user email column"
    And the LLM output contains the rationale sentinel
    When the draft command is invoked
    Then the SQL and rationale are separated at the sentinel
    And each rationale line is written to stderr with "rationale: " prefix

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer receives SQL without rationale
    Given the intent is "add user email column"
    And the LLM output lacks the rationale sentinel
    When the draft command is invoked
    Then all output is treated as SQL
    And no rationale is emitted to stderr

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer receives warning for unparseable SQL
    Given the intent is "add user email column"
    And the LLM generates SQL that fails sqlglot parsing
    When the draft command is invoked
    Then a warning is written to stderr with "warning: " prefix
    And the warning contains the parse exception message

  @pickled-internal:core-llm-cache-default-on
  Scenario Outline: Developer receives warning for destructive operations
    Given the intent is "restructure database"
    And the LLM generates SQL containing "<drop_statement>"
    When the draft command is invoked
    Then a warning is written to stderr identifying the line number
    And the warning advises confirmation before applying

    Examples:
      | drop_statement     |
      | DROP TABLE users   |
      | drop table users   |
      | Drop Table users   |
      | DROP table users   |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer completes draft with validation warnings
    Given the intent is "add user email column"
    And the LLM generates SQL with validation warnings
    When the draft command is invoked
    Then the SQL is emitted to the configured output
    And warnings are written to stderr
    And the process exits with code 1

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer completes draft without validation warnings
    Given the intent is "add user email column"
    And the LLM generates valid SQL without warnings
    When the draft command is invoked
    Then the SQL is emitted to the configured output
    And the process exits with code 0

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM client configuration fails
    Given the LLM client configuration raises a ConfigError with message "Invalid factory"
    When the draft command is invoked
    Then a ClickException is raised with message "Invalid factory"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Unexpected error during draft generation
    Given the intent is "add user email column"
    And an unexpected exception occurs with message "Network timeout"
    When the draft command is invoked
    Then the exception message "Network timeout" is written to stderr
    And the process exits with code 2

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Current schema file does not exist
    Given the intent is "add user email column"
    And the current_schema parameter is "nonexistent.yaml"
    And the file "nonexistent.yaml" does not exist
    When the draft command is invoked
    Then an exception is caught
    And the exception message is written to stderr
    And the process exits with code 2

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Intent file does not exist
    Given the intent is provided as a file path "nonexistent.txt"
    And the file "nonexistent.txt" does not exist
    When the draft command is invoked
    Then an exception is caught
    And the exception message is written to stderr
    And the process exits with code 2
