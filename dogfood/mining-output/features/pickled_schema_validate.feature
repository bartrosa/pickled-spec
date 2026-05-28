Feature: Schema file validation via CLI command
  As a developer using pickled-schema
  I want to validate schema files against their format specifications
  So that I can ensure my schema files are correctly formatted

  Background:
    Given the pickled-schema CLI is available

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer validates an OpenAPI schema with .yaml extension
    Given a file "api-spec.yaml" containing a valid OpenAPI 3.1 schema
    When the developer validates the file
    Then the validation succeeds
    And the output is JSON with valid true and format "openapi_3_1"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer validates an OpenAPI schema with .yml extension
    Given a file "api-spec.yml" containing a valid OpenAPI 3.1 schema
    When the developer validates the file
    Then the validation succeeds
    And the output is JSON with valid true and format "openapi_3_1"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer validates a JSON Schema file
    Given a file "data-schema.json" containing a valid JSON Schema 2020-12
    When the developer validates the file
    Then the validation succeeds
    And the output is JSON with valid true and format "json_schema_2020_12"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer validates a Protocol Buffers file
    Given a file "messages.proto" containing a valid Protocol Buffers 3 schema
    When the developer validates the file
    Then the validation succeeds
    And the output is JSON with valid true and format "proto3"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Developer validates files with case-insensitive extensions
    Given a file "<filename>" containing a valid schema
    When the developer validates the file
    Then the validation succeeds
    And the output is JSON with valid true

    Examples:
      | filename        |
      | spec.YAML       |
      | spec.Yaml       |
      | spec.YML        |
      | spec.JSON       |
      | spec.PROTO      |

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer attempts to validate a file with unrecognized extension
    Given a file "schema.xml" exists
    When the developer validates the file
    Then the command fails with ClickException
    And the error message contains "cannot infer format from extension '.xml'"
    And the error message contains "use --format"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer validates OpenAPI file without openapi-spec-validator installed
    Given a file "api-spec.yaml" containing a valid OpenAPI 3.1 schema
    And the openapi-spec-validator library is not installed
    When the developer validates the file
    Then the command fails with SchemaValidationError
    And the error message is "install pickled-schema[openapi] for OpenAPI validation"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer validates an invalid OpenAPI schema
    Given a file "api-spec.yaml" containing an invalid OpenAPI 3.1 schema
    And the openapi-spec-validator library is installed
    When the developer validates the file
    Then the command fails with SchemaValidationError
    And the error message is "OpenAPI validation failed"
    And the error includes validation details from openapi-spec-validator

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer validates an invalid JSON Schema
    Given a file "data-schema.json" containing an invalid JSON Schema
    When the developer validates the file
    Then the command fails with validation error from validate_json_schema_document

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Developer validates an invalid Protocol Buffers file
    Given a file "messages.proto" containing invalid Protocol Buffers syntax
    When the developer validates the file
    Then the command fails with validation error from parse_proto_file

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: System outputs validation result to standard output
    Given a file "api-spec.yaml" containing a valid OpenAPI 3.1 schema
    When the developer validates the file
    Then the result is written to standard output via click.echo
    And the output is valid JSON

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: System loads OpenAPI file as dictionary for validation
    Given a file "api-spec.yaml" containing a valid OpenAPI 3.1 schema
    When the developer validates the file
    Then the file content is loaded into a dictionary
    And the dictionary is passed to openapi-spec-validator.validate

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: System delegates JSON Schema validation to validate_json_schema_document
    Given a file "data-schema.json" containing a valid JSON Schema 2020-12
    When the developer validates the file
    Then the file is loaded into a dictionary
    And validate_json_schema_document is called with the dictionary

  @best-practices:agent-path-first-class
  Scenario: System delegates Protocol Buffers validation to parse_proto_file
    Given a file "messages.proto" containing a valid Protocol Buffers 3 schema
    When the developer validates the file
    Then parse_proto_file is called with the file path
