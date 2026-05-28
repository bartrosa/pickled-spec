Feature: Data Draft SQL Migration from Intent Tool

  As a developer or automated workflow
  I want to generate SQL migration scripts from natural language descriptions
  So that I can evolve database schemas without writing raw DDL

  Background:
    Given the data_draft_sql_migration_from_intent tool is available

  @data-domain:migration-drift-gate
  Scenario: Developer generates migration with intent and dialect only
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    When the developer invokes the tool with intent_text and dialect
    Then the tool returns valid SQL migration statements
    And the SQL is syntactically valid for postgresql

  @data-domain:migration-drift-gate
  Scenario: Developer generates migration with current schema provided
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    And the current schema is provided in YAML format
      """
      tables:
        users:
          columns:
            - id: integer
            - name: varchar(255)
      """
    When the developer invokes the tool with intent_text, dialect, and current_schema_yaml
    Then the tool returns valid SQL migration statements
    And the migration reflects the transition from current schema to intended state
    And the SQL is syntactically valid for postgresql

  @data-domain:migration-drift-gate
  Scenario Outline: Tool generates dialect-specific SQL syntax
    Given the developer has an intent description "Create orders table with id and amount"
    And the target dialect is "<dialect>"
    When the developer invokes the tool with intent_text and dialect
    Then the tool returns valid SQL migration statements
    And the SQL is syntactically valid for <dialect>

    Examples:
      | dialect    |
      | postgresql |
      | mysql      |
      | sqlite     |

  # TODO: Clarify expected behavior when current_schema_yaml is omitted - verify baseline assumptions from implementation
  @data-domain:migration-drift-gate
  Scenario: Developer omits current schema parameter
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    When the developer invokes the tool without current_schema_yaml
    Then the tool returns valid SQL migration statements

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Tool execution validates against DataContractGate
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    When the developer invokes the tool with intent_text and dialect
    Then DataContractGate.run validation is triggered or respected

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Tool execution validates against MigrationDriftGate
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    And the current schema is provided in YAML format
    When the developer invokes the tool with intent_text, dialect, and current_schema_yaml
    Then MigrationDriftGate.run checks are triggered or respected

  @data-domain:migration-drift-gate
  Scenario: Developer provides required intent_text parameter
    Given the target dialect is "postgresql"
    When the developer invokes the tool with intent_text "Create products table"
    Then the tool accepts the intent_text parameter
    And the tool returns valid SQL migration statements

  @data-domain:migration-drift-gate
  Scenario: Developer provides required dialect parameter
    Given the developer has an intent description "Add email column to users table"
    When the developer invokes the tool with dialect "postgresql"
    Then the tool accepts the dialect parameter
    And the tool returns valid SQL migration statements

  @data-domain:migration-drift-gate
  Scenario: Developer provides optional current_schema_yaml parameter
    Given the developer has an intent description "Add email column to users table"
    And the target dialect is "postgresql"
    And the current schema is provided in YAML format
    When the developer invokes the tool with current_schema_yaml
    Then the tool accepts the current_schema_yaml parameter
    And the migration generation considers the existing schema

  # TODO: Verify from implementation whether ambiguous intent causes error or best-effort generation
  @bdd-domain:gherkin-feature-header-required
  Scenario: Tool handles ambiguous intent description
    Given the developer has an ambiguous intent description "Change the user thing"
    And the target dialect is "postgresql"
    When the developer invokes the tool with intent_text and dialect
    Then the tool responds with error or best-effort SQL generation

  # TODO: Verify from implementation whether conflicting intent causes error or resolution strategy
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Tool handles conflicting intent description
    Given the developer has a conflicting intent description "Add email column and remove email column from users"
    And the target dialect is "postgresql"
    When the developer invokes the tool with intent_text and dialect
    Then the tool responds with error or resolved SQL generation
