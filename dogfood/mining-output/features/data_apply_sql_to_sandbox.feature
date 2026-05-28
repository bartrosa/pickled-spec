Feature: Apply SQL to Sandbox
  As a data engineer
  I want to execute SQL statements against an in-memory SQLite database
  So that I can validate queries and explore schema changes without affecting persistent data

  Scenario: User executes valid CREATE TABLE statement
    When the user applies SQL to create a single table
    Then the schema information includes the created table name
    And the schema information includes column definitions for the table

  Scenario: User executes multiple SQL statements
    When the user applies SQL to create a table and then alter it
    Then the schema information reflects the final database state after all statements

  Scenario: User executes invalid SQL
    When the user applies SQL with syntax errors
    Then an error response is returned
    And no schema output is provided

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: User executes SQL that creates no tables
    When the user applies SQL that does not create any tables
    Then an empty or minimal schema representation is returned

  Scenario: User executes DROP TABLE statement
    When the user applies SQL to create a table and then drop it
    Then the dropped table is not present in the returned schema

  @best-practices:agent-path-first-class
  Scenario: User invokes the tool multiple times
    When the user applies SQL to create a table in the first invocation
    And the user applies different SQL in a second invocation
    Then the second invocation's schema does not include tables from the first invocation

  Scenario Outline: User provides optional dialect parameter
    When the user applies SQL with dialect set to "<dialect>"
    Then the SQL is executed without error
    And schema information is returned

    Examples:
      | dialect   |
      | sqlite    |
      | postgres  |
      | mysql     |

  @oss-hygiene:no-secrets-in-repo
  Scenario Outline: Schema output format consistency
    When the user applies SQL that "<sql_description>"
    Then the returned schema format is consistent and parseable

    Examples:
      | sql_description                      |
      | creates a simple table               |
      | creates multiple tables              |
      | creates a table with complex types   |
      | creates tables with foreign keys     |
