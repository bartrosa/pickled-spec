Feature: Check migration drift against expected schema
  As a developer or CI/CD pipeline
  I want to validate that a migration produces the expected database schema
  So that I can detect drift between documented expectations and actual migration behavior

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration against expected schema with drift detected
    Given a migration script "001_create_users_table"
    And an expected schema YAML file "expected_users_schema.yaml"
    When the developer runs check-drift with the migration and expected schema
    Then MigrationDriftGate is executed with the migration and expected schema
    And drift is reported between the migration output and expected schema
    And the command exits with a failure status code

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration against expected schema without drift
    Given a migration script "002_create_orders_table"
    And an expected schema YAML file "expected_orders_schema.yaml"
    And the migration produces a schema matching the expected schema
    When the developer runs check-drift with the migration and expected schema
    Then MigrationDriftGate is executed with the migration and expected schema
    And validation success is reported
    And the command exits with a success status code

  @data-domain:migration-drift-gate
  Scenario: Developer validates migration with specific database dialect
    Given a migration script "003_create_products_table"
    And an expected schema YAML file "expected_products_schema.yaml"
    And a database dialect "postgresql"
    When the developer runs check-drift with the migration, expected schema, and dialect
    Then MigrationDriftGate is executed with the migration, expected schema, and dialect
    And validation results are reported
    And the command exits with an appropriate status code

  @data-domain:migration-drift-gate
  Scenario: CI/CD pipeline validates migration without optional dialect parameter
    Given a migration script "004_create_inventory_table"
    And an expected schema YAML file "expected_inventory_schema.yaml"
    When the CI/CD pipeline runs check-drift with only the required parameters
    Then MigrationDriftGate is executed with the migration and expected schema
    And validation results are reported
    And the command exits with an appropriate status code

  @data-domain:migration-drift-gate
  Scenario: Developer attempts to run check-drift without required migration argument
    Given an expected schema YAML file "expected_schema.yaml"
    When the developer runs check-drift without the migration argument
    Then the command reports a missing required argument error
    And the command exits with a failure status code

  @data-domain:migration-drift-gate
  Scenario: Developer attempts to run check-drift without required expected schema argument
    Given a migration script "005_create_customers_table"
    When the developer runs check-drift without the expected schema argument
    Then the command reports a missing required argument error
    And the command exits with a failure status code

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer invokes check-drift from command line as part of pickled-data CLI
    Given a migration script "006_create_payments_table"
    And an expected schema YAML file "expected_payments_schema.yaml"
    When the developer invokes "pickled-data check-drift" from the command line
    Then the command executes successfully as part of the pickled-data CLI
    And MigrationDriftGate is executed with the provided parameters
    And validation results are reported
    And the command exits with an appropriate status code
