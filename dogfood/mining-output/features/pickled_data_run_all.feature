Feature: Data project migration quality checks
  As a data quality engineer
  I want to validate SQL migrations and schema drift in my data project
  So that I can ensure migrations are parseable and produce the expected schema

  Background:
    Given a data project working directory

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Project with no migration files returns a warning
    Given the migrations directory is empty
    When the migration quality checks run
    Then exactly one gate result is returned
    And the gate result has verdict "WARN"
    And the gate result has gate_name "data.migrations"
    And the gate result notes indicate no migrations were found

  @data-domain:migration-drift-gate
  Scenario: Project with no expected schema file skips drift check
    Given migration file "001_create_table.sql" exists and is valid SQL
    And the expected_schema.yaml file does not exist
    When the migration quality checks run
    Then the results do not include a gate result with gate_name "data.migration_drift"

  @data-domain:migration-drift-gate
  Scenario: Project with expected schema as a non-file skips drift check
    Given migration file "001_create_table.sql" exists and is valid SQL
    And expected_schema.yaml exists but is a directory
    When the migration quality checks run
    Then the results do not include a gate result with gate_name "data.migration_drift"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Migration file with parse error returns a failure
    Given migration file "002_bad_syntax.sql" contains unparseable SQL
    When the migration quality checks run
    Then a gate result with gate_name "data.parse.002_bad_syntax.sql" has verdict "FAIL"
    And that gate result notes contain the parse error message

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Migration file with valid SQL returns a pass
    Given migration file "003_valid.sql" contains valid SQLite SQL
    When the migration quality checks run
    Then a gate result with gate_name "data.parse.003_valid.sql" has verdict "PASS"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Project with exactly one migration does not warn about multiple migrations
    Given migration file "001_single.sql" exists and is valid SQL
    When the migration quality checks run
    Then the results do not include a gate result with gate_name "data.migrations.note"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Project with multiple migrations warns about application order
    Given migration file "001_first.sql" exists and is valid SQL
    And migration file "002_second.sql" exists and is valid SQL
    When the migration quality checks run
    Then a gate result with gate_name "data.migrations.note" has verdict "WARN"
    And that gate result notes explain migrations will be applied in filename order

  @data-domain:migration-drift-gate
  Scenario: Project with migrations and valid expected schema runs drift check
    Given migration file "001_create.sql" exists and is valid SQL
    And expected_schema.yaml exists and contains a valid dictionary
    When the migration quality checks run
    Then a gate result with gate_name "data.migration_drift" is included

  @data-domain:migration-drift-gate
  Scenario: All SQL parsing uses SQLite dialect
    Given migration file "001_migration.sql" contains SQL
    When the migration quality checks run
    Then the SQL is parsed using "sqlite" dialect
    And the drift check receives dialect "sqlite" in context

  @best-practices:agent-path-first-class
  Scenario Outline: Migration files are processed in lexicographic order
    Given migration file "<first>" exists and is valid SQL
    And migration file "<second>" exists and is valid SQL
    And migration file "<third>" exists and is valid SQL
    When the migration quality checks run
    Then migrations are processed in order "<first>", "<second>", "<third>"

    Examples:
      | first       | second      | third       |
      | 001_a.sql   | 002_b.sql   | 003_c.sql   |
      | 1_early.sql | 10_late.sql | 2_middle.sql|

  @data-domain:migration-drift-gate
  Scenario: Combined SQL for drift check concatenates with double newlines
    Given migration file "001_first.sql" contains "CREATE TABLE a;"
    And migration file "002_second.sql" contains "CREATE TABLE b;"
    And expected_schema.yaml exists and contains a valid dictionary
    When the migration quality checks run
    Then the drift gate receives combined SQL "CREATE TABLE a;\n\nCREATE TABLE b;"

  @data-domain:migration-drift-gate
  Scenario: YAML file with non-dict content skips drift check without error
    Given migration file "001_create.sql" exists and is valid SQL
    And expected_schema.yaml exists and contains a list
    When the migration quality checks run
    Then the results do not include a gate result with gate_name "data.migration_drift"
    And no exception is raised

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Multiple migration files produce multiple parse results
    Given migration file "001_first.sql" is <first_status>
    And migration file "002_second.sql" is <second_status>
    And migration file "003_third.sql" is <third_status>
    When the migration quality checks run
    Then a gate result with gate_name "data.parse.001_first.sql" has verdict "<first_verdict>"
    And a gate result with gate_name "data.parse.002_second.sql" has verdict "<second_verdict>"
    And a gate result with gate_name "data.parse.003_third.sql" has verdict "<third_verdict>"

    Examples:
      | first_status | second_status | third_status | first_verdict | second_verdict | third_verdict |
      | valid SQL    | valid SQL     | valid SQL    | PASS          | PASS           | PASS          |
      | valid SQL    | invalid SQL   | valid SQL    | PASS          | FAIL           | PASS          |
      | invalid SQL  | invalid SQL   | invalid SQL  | FAIL          | FAIL           | FAIL          |

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Working directory is resolved to absolute path
    Given a relative path to the working directory
    When the migration quality checks run
    Then the working directory is resolved to an absolute path before processing

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Function always returns at least one gate result
    Given any valid working directory configuration
    When the migration quality checks run
    Then at least one gate result is returned
