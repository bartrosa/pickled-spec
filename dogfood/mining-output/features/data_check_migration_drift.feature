Feature: Data Check Migration Drift
  As a development team member
  I want to validate that SQL migration scripts produce the expected database schema
  So that I can catch schema drift before deploying migrations to production

  Background:
    Given a migration drift validation tool is available

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration script matches expected schema
    Given a SQL migration script that creates tables with specific columns
    And an expected schema definition in YAML format that matches the migration
    When the migration drift check is performed
    Then the result indicates the migration matches the expected schema
    And no drift is reported

  @data-domain:migration-drift-gate
  Scenario: Developer detects schema drift when migration differs from expected schema
    Given a SQL migration script that creates tables with specific columns
    And an expected schema definition in YAML format that differs from the migration
    When the migration drift check is performed
    Then the result indicates drift between the migration and expected schema
    And the drift details are included in the result

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration with specific SQL dialect
    Given a SQL migration script written in PostgreSQL dialect
    And an expected schema definition in YAML format
    And the SQL dialect is specified as "postgresql"
    When the migration drift check is performed with the specified dialect
    Then the migration is parsed and executed using PostgreSQL dialect rules
    And the result indicates whether the migration matches the expected schema

  @data-domain:migration-drift-gate
  Scenario Outline: Developer validates migrations across different SQL dialects
    Given a SQL migration script written in <dialect> syntax
    And an expected schema definition in YAML format
    And the SQL dialect is specified as "<dialect>"
    When the migration drift check is performed with the specified dialect
    Then the migration is processed according to <dialect> rules
    And the result indicates whether the migration matches the expected schema

    Examples:
      | dialect    |
      | postgresql |
      | mysql      |
      | sqlite     |
      | sqlserver  |

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration without specifying dialect
    Given a SQL migration script in standard SQL syntax
    And an expected schema definition in YAML format
    When the migration drift check is performed without specifying a dialect
    Then a default SQL dialect is used for validation
    And the result indicates whether the migration matches the expected schema

  @data-domain:migration-drift-gate
  Scenario: Developer receives actionable results for CI/CD pipeline integration
    Given a SQL migration script
    And an expected schema definition in YAML format
    When the migration drift check is performed
    Then the result format is suitable for programmatic consumption
    And the result clearly indicates migration validity status
    And the result can be used to pass or fail a CI/CD pipeline step

  @data-domain:migration-drift-gate
  Scenario: Validation fails when required SQL parameter is missing
    Given an expected schema definition in YAML format
    When the migration drift check is performed without providing SQL
    Then the validation fails with an error indicating SQL is required

  @data-domain:migration-drift-gate
  Scenario: Validation fails when required expected schema parameter is missing
    Given a SQL migration script
    When the migration drift check is performed without providing expected schema YAML
    Then the validation fails with an error indicating expected schema is required
