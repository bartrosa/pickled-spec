Feature: Parse migration SQL files into AST summaries

  As a developer or CI/CD tool
  I want to parse migration SQL files and view their structure as JSON
  So that I can inspect, validate, and debug migrations before execution

  Background:
    Given the parse command is available in the pickled-data CLI

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses a valid PostgreSQL migration file
    Given a migration file "001_create_users.sql" with valid PostgreSQL DDL
    When the developer parses the file without specifying a dialect
    Then the command reads the file using UTF-8 encoding
    And the command parses the SQL using "postgres" dialect
    And the command outputs valid JSON to stdout
    And the JSON contains the key "dialect" with value "postgres"
    And the JSON contains the key "kind" with the AST root node class name
    And the JSON contains the key "sql" with the SQL rendered in "postgres" dialect
    And the JSON is indented with 2 spaces
    And the command returns None

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses a migration file with an explicit dialect
    Given a migration file "002_add_index.sql" with valid SQL
    When the developer parses the file specifying dialect "mysql"
    Then the command parses the SQL using "mysql" dialect
    And the JSON output contains the key "dialect" with value "mysql"
    And the JSON contains the key "sql" with the SQL rendered in "postgres" dialect

  @rules-domain:coverage-union-across-features
  Scenario: Developer attempts to parse a DBT file
    Given a file "transform.sql.dbt" exists
    When the developer attempts to parse the file
    Then the command raises NotImplementedError before reading the file
    And the error message indicates DBT files are not supported

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer parses a file with unparseable SQL
    Given a migration file "invalid.sql" with malformed SQL that sqlglot cannot parse
    When the developer attempts to parse the file
    Then the command raises SQLParseError
    And the error message contains details from the original sqlglot ParseError

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses a file that results in empty parse output
    Given a migration file "empty_parse.sql" that causes sqlglot to return None
    When the developer attempts to parse the file
    Then the command raises SQLParseError with message "empty parse result"

  @best-practices:agent-path-first-class
  Scenario Outline: File I/O errors propagate without wrapping
    Given a migration file path "<file_path>"
    And the file condition is <condition>
    When the developer attempts to parse the file
    Then the command propagates <exception_type> without wrapping

    Examples:
      | file_path           | condition         | exception_type       |
      | nonexistent.sql     | does not exist    | FileNotFoundError    |
      | restricted.sql      | no read permission| PermissionError      |

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Parse command output structure validation
    Given a migration file "003_alter_table.sql" with valid SQL
    When the developer parses the file
    Then the JSON output contains exactly three keys: "dialect", "kind", and "sql"
    And all three keys have non-empty string values
    And the output is written to standard output via click.echo

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: SQL output is always rendered in postgres dialect
    Given a migration file "004_select.sql" with valid SQL
    When the developer parses the file specifying dialect "snowflake"
    Then the JSON key "dialect" contains "snowflake"
    But the JSON key "sql" contains SQL rendered in "postgres" dialect
