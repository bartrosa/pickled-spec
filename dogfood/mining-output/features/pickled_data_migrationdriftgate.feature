Feature: Migration Drift Gate Validation
  As a migration validation pipeline
  I want to verify SQL migrations produce expected database schemas
  So that I can detect drift before deployment

  Background:
    Given the MigrationDriftGate is initialized

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Developer provides non-string target
    Given the target is an integer value 42
    When the gate runs
    Then the verdict is FAIL
    And the notes contain the type name "int"

  @data-domain:migration-drift-gate
  Scenario: Developer provides context without expected schema
    Given the target is a valid SQL migration string
    And the context does not contain "expected_schema"
    And the context does not contain "expected_schema_yaml"
    When the gate runs
    Then the verdict is FAIL
    And the notes describe missing schema context

  @data-domain:migration-drift-gate
  Scenario: Developer provides expected schema as a dictionary
    Given the target is a valid SQL migration string
    And the context contains "expected_schema" as a dictionary with table definitions
    When the gate runs
    Then the expected schema is used directly without YAML parsing

  @data-domain:migration-drift-gate
  Scenario: Developer provides expected schema as YAML string
    Given the target is a valid SQL migration string
    And the context contains "expected_schema_yaml" as a valid YAML string
    When the gate runs
    Then the YAML is parsed via yaml.safe_load
    And the parsed dictionary is used as the expected schema

  @data-domain:migration-drift-gate
  Scenario: Developer provides YAML that parses to non-dictionary
    Given the target is a valid SQL migration string
    And the context contains "expected_schema_yaml" that parses to a list
    When the gate runs
    Then the verdict is FAIL
    And the notes describe invalid context

  @data-domain:migration-drift-gate
  Scenario: Migration produces schema with different tables than expected
    Given the target is SQL creating tables "users" and "orders"
    And the expected schema defines tables "users" and "products"
    When the gate runs
    Then the verdict is FAIL
    And the notes list expected table names
    And the notes list actual table names

  @data-domain:migration-drift-gate
  Scenario: Migration produces table with different columns than expected
    Given the target is SQL creating table "users" with columns "id" and "name"
    And the expected schema defines table "users" with columns "id" and "email"
    When the gate runs
    Then the verdict is FAIL
    And the notes identify the table "users"
    And the notes list expected column set
    And the notes list actual column set

  @data-domain:migration-drift-gate
  Scenario: Migration produces schema matching expected exactly
    Given the target is SQL creating table "users" with columns matching expected types and nullability
    And the expected schema defines the same structure
    When the gate runs
    Then the verdict is PASS
    And the notes are "Schema matches expected."

  @data-domain:migration-drift-gate
  Scenario: Migration produces schema with only nullable differences
    Given the target is SQL creating table "users" with column "name" as nullable
    And the expected schema defines column "name" as not nullable
    When the gate runs
    Then the verdict is PASS
    And the notes describe nullable differences

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: SQL dialect is specified in context
    Given the target is a SQL string in MySQL dialect
    And the context contains "dialect" with value "mysql"
    When the gate runs
    Then the SQL is parsed using MySQL dialect
    And the SQL is transpiled to SQLite dialect for execution

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: SQL dialect defaults to postgres when not specified
    Given the target is a SQL string
    And the context does not contain "dialect"
    When the gate runs
    Then the SQL is parsed using postgres dialect

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Column types are normalized to uppercase during comparison
    Given the target is SQL creating column "id" with type "integer"
    And the expected schema defines column "id" with type "INTEGER"
    When the gate runs
    Then the column types are normalized to uppercase before comparison

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Nullable defaults to true when not specified
    Given the target is SQL creating column "name" without explicit nullable constraint
    And the expected schema defines column "name" without explicit nullable
    When the gate runs
    Then nullable is treated as True for both schemas

  @data-domain:migration-drift-gate
  Scenario: SQLite connection is closed after successful execution
    Given the target is a valid SQL migration string
    And the expected schema matches the migration output
    When the gate runs
    Then the SQLite connection is closed

  @data-domain:migration-drift-gate
  Scenario: SQLite connection is closed after failed execution
    Given the target is a valid SQL migration string
    And the migration fails during execution
    When the gate runs
    Then the SQLite connection is closed in the finally block

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Empty SQL statements are skipped during transpilation
    Given the target contains empty statements between valid SQL
    And the expected schema matches the valid SQL output
    When the gate runs
    Then empty statements are skipped
    And only valid statements are transpiled and executed

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: None statements from parsing are skipped
    Given the SQL parser returns None for certain statements
    And the target contains valid SQL statements
    When the gate runs
    Then None statements are skipped during transpilation

  @data-domain:migration-drift-gate
  Scenario: SQLite attachment limit is set to prevent ATTACH statements
    Given the target is a SQL migration string
    When the gate runs
    Then the SQLite connection attachment limit is set to 0
