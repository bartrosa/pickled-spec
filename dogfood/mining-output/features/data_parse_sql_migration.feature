Feature: Parse SQL migration files into AST summary
  As a data engineer or migration author
  I want to parse SQL migration files into structured AST representations
  So that I can programmatically analyze schema changes for drift detection

  @data-domain:migration-drift-gate
  Scenario: Data engineer parses valid CREATE TABLE statement
    Given a SQL migration containing a CREATE TABLE statement
    When the data engineer parses the SQL
    Then the tool returns an AST summary structure
    And the AST summary represents the CREATE TABLE command

  @data-domain:migration-drift-gate
  Scenario: Data engineer parses valid ALTER TABLE statement
    Given a SQL migration containing an ALTER TABLE statement
    When the data engineer parses the SQL
    Then the tool returns an AST summary structure
    And the AST summary represents the ALTER TABLE command

  @data-domain:migration-drift-gate
  Scenario: Data engineer parses SQL with specific dialect
    Given a SQL migration written in PostgreSQL dialect
    When the data engineer parses the SQL with dialect "postgresql"
    Then the tool returns an AST summary structure
    And the SQL is parsed according to PostgreSQL syntax rules

  @data-domain:migration-drift-gate
  Scenario: Data engineer parses SQL without specifying dialect
    Given a SQL migration containing standard SQL syntax
    When the data engineer parses the SQL without specifying a dialect
    Then the tool returns an AST summary structure
    And the SQL is parsed using default dialect rules

  @data-domain:migration-drift-gate
  Scenario: Drift detection gate consumes AST output
    Given a SQL migration that has been parsed
    When the AST summary is provided to a drift detection gate
    Then the drift detection gate can analyze the structured output

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Data engineer parses empty SQL input
    Given an empty SQL string
    When the data engineer parses the SQL
    Then the tool handles the empty input gracefully
    And the tool returns an appropriate response for empty input

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Data engineer parses whitespace-only SQL input
    Given a SQL string containing only whitespace
    When the data engineer parses the SQL
    Then the tool handles the whitespace-only input gracefully
    And the tool returns an appropriate response for whitespace input

  @data-domain:migration-drift-gate
  Scenario: Data engineer attempts to parse malformed SQL
    Given a SQL migration with syntax errors
    When the data engineer parses the SQL
    Then the tool reports a parse error
    And the error indicates the malformed syntax

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Data engineer parses SQL without required parameter
    Given no SQL text is provided
    When the data engineer attempts to parse
    Then the tool reports that the sql parameter is required

  @data-domain:migration-drift-gate
  Scenario Outline: Data engineer parses various SQL migration statements
    Given a SQL migration containing a <statement_type> statement
    When the data engineer parses the SQL
    Then the tool returns an AST summary structure
    And the AST summary represents the <statement_type> command

    Examples:
      | statement_type |
      | CREATE TABLE   |
      | ALTER TABLE    |
      | DROP TABLE     |
      | CREATE INDEX   |
      | DROP INDEX     |
