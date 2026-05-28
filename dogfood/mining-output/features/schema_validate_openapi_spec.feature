Feature: Validate OpenAPI specification documents
  As an MCP client
  I want to validate OpenAPI specification documents in YAML format
  So that I can ensure API specifications conform to OpenAPI standards before using them

  @schema-domain:openapi-validate-deterministic
  Scenario: MCP client validates a valid OpenAPI 3.x YAML document
    Given a valid OpenAPI 3.x YAML document
    When the client validates the OpenAPI specification
    Then the validation completes without errors
    And the validation output indicates the specification conforms to OpenAPI standards

  @schema-domain:openapi-validate-deterministic
  Scenario: MCP client validates an invalid OpenAPI YAML document
    Given an invalid OpenAPI YAML document
    When the client validates the OpenAPI specification
    Then the validation reports specific validation failures
    And the validation output indicates the specification does not conform to OpenAPI standards

  @schema-domain:openapi-validate-deterministic
  Scenario: MCP client validates malformed YAML
    Given a malformed YAML document
    When the client validates the OpenAPI specification
    Then the validation reports a parsing error

  @schema-domain:openapi-validate-deterministic
  Scenario: MCP client validates an empty string
    Given an empty string as the spec_yaml parameter
    When the client validates the OpenAPI specification
    Then the validation reports a validation error

  @schema-domain:openapi-validate-deterministic
  Scenario: MCP client invokes validation without required spec_yaml parameter
    Given the spec_yaml parameter is omitted
    When the client attempts to validate the OpenAPI specification
    Then the tool fails due to missing required parameter
