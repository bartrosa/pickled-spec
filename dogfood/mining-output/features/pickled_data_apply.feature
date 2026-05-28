Feature: Apply migration to in-memory SQLite database
  As a developer or automated tool
  I want to validate SQL migration files in a sandbox environment
  So that I can verify migrations will execute successfully before applying them to production

  Background:
    Given an in-memory SQLite database is available

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer applies a valid migration file
    Given a migration file "001_create_users.sql" containing valid SQL
    And the dialect is "postgres"
    When the developer applies the migration
    Then the migration executes successfully
    And JSON output is printed to stdout
    And the JSON contains a "tables" array
    And the JSON is indented with 2 spaces

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer applies migration creating tables with columns
    Given a migration file "002_schema.sql" creating table "users" with columns:
      | name     | type    | nullable |
      | id       | INTEGER | false    |
      | email    | VARCHAR | false    |
      | nickname | TEXT    | true     |
    And the dialect is "postgres"
    When the developer applies the migration
    Then the JSON output contains a table object with name "users"
    And the table object contains a "columns" array
    And the columns array contains a column with name "id", type "INTEGER", and nullable false
    And the columns array contains a column with name "email", type "VARCHAR", and nullable false
    And the columns array contains a column with name "nickname", type "TEXT", and nullable true

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer applies migration with column types needing uppercasing
    Given a migration file "003_types.sql" creating table "items" with column "status" of type "varchar"
    And the dialect is "postgres"
    When the developer applies the migration
    Then the JSON output contains a column with type "VARCHAR"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer applies migration creating column with null type
    Given a migration file "004_null_type.sql" creating a column with null type reported by database
    And the dialect is "postgres"
    When the developer applies the migration
    Then the JSON output contains a column with type "TEXT"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: System excludes SQLite internal tables from output
    Given a migration file "005_tables.sql" creating table "products"
    And the dialect is "postgres"
    And SQLite system tables exist with names starting with "sqlite_"
    When the developer applies the migration
    Then the JSON output contains a table with name "products"
    And the JSON output does not contain any table with name starting with "sqlite_"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer attempts to apply a dbt migration file
    Given a migration file "001_model.dbt" containing valid SQL
    And the dialect is "postgres"
    When the developer applies the migration
    Then a NotImplementedError is raised
    And the error message indicates dbt is not implemented
    And no SQL processing occurs

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration with top-level ATTACH statement
    Given a migration file "malicious.sql" containing a top-level ATTACH statement
    And the dialect is "postgres"
    When the developer applies the migration
    Then an UnsafeMigrationStatementError is raised
    And no database connection is created

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration with nested ATTACH statement
    Given a migration file "nested_attach.sql" containing a nested ATTACH statement
    And the dialect is "postgres"
    When the developer applies the migration
    Then an UnsafeMigrationStatementError is raised
    And no database connection is created

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration with top-level DETACH statement
    Given a migration file "detach.sql" containing a top-level DETACH statement
    And the dialect is "postgres"
    When the developer applies the migration
    Then an UnsafeMigrationStatementError is raised
    And no database connection is created

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration with nested DETACH statement
    Given a migration file "nested_detach.sql" containing a nested DETACH statement
    And the dialect is "postgres"
    When the developer applies the migration
    Then an UnsafeMigrationStatementError is raised
    And no database connection is created

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration with unparseable SQL
    Given a migration file "invalid.sql" containing SQL that cannot be parsed
    And the dialect is "postgres"
    When the developer applies the migration
    Then a SQLParseError is raised

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Developer applies an empty migration file
    Given a migration file "empty.sql" that is empty
    And the dialect is "postgres"
    When the developer applies the migration
    Then a SQLParseError is raised

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration file with no parse result
    Given a migration file "no_result.sql" that produces no parse result
    And the dialect is "postgres"
    When the developer applies the migration
    Then a SQLParseError is raised

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: System handles statement execution failure gracefully
    Given a migration file "failing.sql" with SQL that fails during execution
    And the dialect is "postgres"
    When the developer applies the migration
    Then the statement execution fails
    And the database connection is closed

  @data-domain:migration-drift-gate
  Scenario: Developer applies migration file with invalid UTF-8 encoding
    Given a migration file "bad_encoding.sql" that is not valid UTF-8
    And the dialect is "postgres"
    When the developer applies the migration
    Then an encoding error is raised

  @data-domain:migration-drift-gate
  Scenario: System transpiles SQL from source dialect to SQLite
    Given a migration file "postgres_specific.sql" containing PostgreSQL-specific SQL
    And the dialect is "postgres"
    When the developer applies the migration
    Then the SQL is transpiled from postgres dialect to SQLite dialect
    And the transpiled SQL is executed in SQLite

  @data-domain:migration-drift-gate
  Scenario: System creates in-memory database not file-based
    Given a migration file "006_memory_test.sql" containing valid SQL
    And the dialect is "postgres"
    When the developer applies the migration
    Then an in-memory SQLite database is used
    And no database file is created on the filesystem

  @best-practices:llm-drafter-temperature-zero
  Scenario: System attempts to set attached database limit to zero
    Given a migration file "007_limit_test.sql" containing valid SQL
    And the dialect is "postgres"
    When the developer applies the migration
    Then the system attempts to set SQLite attached database limit to 0
    And execution continues successfully regardless of AttributeError

  @data-domain:migration-drift-gate
  Scenario: System commits transaction after successful execution
    Given a migration file "008_transaction.sql" containing multiple valid statements
    And the dialect is "postgres"
    When the developer applies the migration
    Then all statements are executed
    And the transaction is committed
    And the schema changes are persisted in memory
