Feature: DataContractGate validates SQL query columns against OpenAPI response properties

  Background:
    Given a DataContractGate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Target is not a string
    When the gate runs with a non-string target
    Then the verdict is FAIL
    And the notes describe the actual type received

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Context is missing endpoint_tag key
    When the gate runs with a string target and context without "endpoint_tag"
    Then the verdict is FAIL
    And the notes indicate the missing endpoint_tag

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Context endpoint_tag value is not a string
    When the gate runs with a string target and endpoint_tag that is not a string
    Then the verdict is FAIL
    And the notes indicate the endpoint_tag must be a string

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: No SchemaRegistry is configured
    Given the gate has no SchemaRegistry configured
    When the gate runs with a valid string target and valid endpoint_tag
    Then the verdict is WARN
    And the notes state "no SchemaRegistry configured"

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Schema artifact not found for endpoint_tag
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry cannot find a schema for the given endpoint_tag
    When the gate runs with a valid string target and valid endpoint_tag
    Then the verdict is WARN
    And the notes include the endpoint_tag name

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: OpenAPI schema has no extractable properties
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact
    And the schema artifact has no extractable properties for 200 or 201 responses
    When the gate runs with a valid SQL query and valid endpoint_tag
    Then the verdict is WARN
    And the notes indicate no properties were found

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: SQL parsing fails
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact with properties
    When the gate runs with an unparseable SQL string and valid endpoint_tag
    Then the gate treats the SQL as having zero columns
    And the validation continues with an empty column set

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: SQL column names exactly match API property names
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact with properties
    When the gate runs with a SQL query whose column names exactly match the API properties
    Then the verdict is PASS
    And the notes state that types are not checked in v0.1

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario Outline: SQL columns differ from API properties
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact with properties <api_properties>
    When the gate runs with a SQL query having columns <sql_columns>
    Then the verdict is FAIL
    And the notes include a sorted list of missing columns
    And the notes include a sorted list of extra columns

    Examples:
      | sql_columns      | api_properties   |
      | id, name         | id, name, email  |
      | id, name, status | id, name         |
      | user_id          | id               |

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: OpenAPI property extraction examines only 200 or 201 response codes
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact with multiple response codes
    When the gate extracts properties from the OpenAPI schema
    Then only properties from 200 or 201 responses are considered

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: OpenAPI property extraction returns names from first matching operation
    Given the gate has a SchemaRegistry configured
    And the SchemaRegistry returns a schema artifact with multiple operations
    When the gate extracts properties from the OpenAPI schema
    Then properties are taken from the first matching operation found

  @pickled-internal:core-llm-cache-default-on
  Scenario: GateResult includes gate name and notes
    Given the gate has a name
    When the gate runs with any valid inputs
    Then the GateResult includes the gate's name
    And the GateResult includes descriptive notes
