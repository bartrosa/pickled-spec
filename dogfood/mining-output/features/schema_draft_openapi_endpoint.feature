Feature: Schema draft OpenAPI endpoint tool
  As an API documentation engineer
  I want to generate OpenAPI 3.1 path items from Gherkin scenarios
  So that I can convert behavioral specifications into machine-readable API schema

  Background:
    Given the schema_draft_openapi_endpoint tool is available

  @schema-domain:openapi-validate-deterministic
  Scenario: Client generates OpenAPI path item from complete Gherkin scenario
    Given the HTTP method is "GET"
    And the endpoint path is "/users/{id}"
    And the Gherkin text describes a user retrieval scenario
    When the client invokes the tool with method, path, and gherkin_text
    Then the tool returns a response containing an OpenAPI path item structure
    And the path item conforms to OpenAPI 3.1 schema specifications
    And the path item corresponds to the "GET" method
    And the path item corresponds to the "/users/{id}" path

  @best-practices:agent-path-first-class
  Scenario: Client attempts to generate path item without required method parameter
    Given the endpoint path is "/users/{id}"
    And the Gherkin text describes a user retrieval scenario
    When the client invokes the tool without the method parameter
    Then the tool returns an error indicating the method parameter is required

  @best-practices:agent-path-first-class
  Scenario: Client attempts to generate path item without required path parameter
    Given the HTTP method is "POST"
    And the Gherkin text describes a user creation scenario
    When the client invokes the tool without the path parameter
    Then the tool returns an error indicating the path parameter is required

  @best-practices:agent-path-first-class
  Scenario: Client attempts to generate path item without required gherkin_text parameter
    Given the HTTP method is "DELETE"
    And the endpoint path is "/users/{id}"
    When the client invokes the tool without the gherkin_text parameter
    Then the tool returns an error indicating the gherkin_text parameter is required

  @best-practices:agent-path-first-class
  Scenario: Gherkin text content influences drafted path item structure
    Given the HTTP method is "POST"
    And the endpoint path is "/orders"
    And the Gherkin text describes request parameters, response codes, and data schemas
    When the client invokes the tool with method, path, and gherkin_text
    Then the returned path item structure reflects elements parsed from the Gherkin text
    And the path item includes parameters derived from the Gherkin scenario
    And the path item includes responses derived from the Gherkin scenario

  @schema-domain:openapi-validate-deterministic
  Scenario Outline: Client generates path items for different HTTP methods
    Given the HTTP method is "<method>"
    And the endpoint path is "<path>"
    And the Gherkin text describes an endpoint scenario
    When the client invokes the tool with method, path, and gherkin_text
    Then the tool returns a response containing an OpenAPI path item structure
    And the path item corresponds to the "<method>" method
    And the path item corresponds to the "<path>" path

    Examples:
      | method | path            |
      | GET    | /products       |
      | POST   | /products       |
      | PUT    | /products/{id}  |
      | PATCH  | /products/{id}  |
      | DELETE | /products/{id}  |

  # TODO: Clarify how SchemaAmbiguityGate integration affects the tool's response
  @best-practices:agent-path-first-class
  Scenario: Tool integrates with SchemaAmbiguityGate during drafting process
    Given the HTTP method is "GET"
    And the endpoint path is "/items"
    And the Gherkin text contains potentially ambiguous schema definitions
    When the client invokes the tool with method, path, and gherkin_text
    Then the SchemaAmbiguityGate is invoked as part of the drafting process

  # TODO: Clarify how SchemaCoverageGate integration affects the tool's response
  @best-practices:agent-path-first-class
  Scenario: Tool integrates with SchemaCoverageGate during drafting process
    Given the HTTP method is "POST"
    And the endpoint path is "/items"
    And the Gherkin text describes partial endpoint behavior
    When the client invokes the tool with method, path, and gherkin_text
    Then the SchemaCoverageGate is invoked as part of the drafting process
