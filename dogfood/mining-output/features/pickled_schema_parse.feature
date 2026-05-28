```gherkin
Feature: Parse schema file metadata
  As an operator or developer
  I want to quickly inspect a schema file's metadata
  So that I can verify format and see basic statistics without full validation

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer parses OpenAPI YAML file without format argument
    Given a valid OpenAPI 3.1 YAML file exists at "spec.yaml"
    When the developer runs parse command with file "spec.yaml" and no format argument
    Then the command outputs JSON to stdout
    And the JSON field "format" matches the detected OpenAPI version from file content
    And the JSON field "endpoint_id" is null
    And the JSON field "source" is "file"
    And the JSON field "content_bytes" equals the UTF-8 byte length of the file content

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses JSON Schema file without format argument
    Given a valid JSON Schema file exists at "schema.json"
    And the JSON root element is an object
    When the developer runs parse command with file "schema.json" and no format argument
    Then the command outputs JSON to stdout
    And the JSON field "format" is "json_schema_2020_12"
    And the JSON field "endpoint_id" is null
    And the JSON field "source" is "file"
    And the JSON field "content_bytes" equals the UTF-8 byte length of the file content

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses Proto3 file without format argument
    Given a valid Proto3 file exists at "service.proto"
    When the developer runs parse command with file "service.proto" and no format argument
    Then the command outputs JSON to stdout
    And the JSON field "format" is "proto3"
    And the JSON field "endpoint_id" is null
    And the JSON field "source" is "file"
    And the JSON field "content_bytes" equals the UTF-8 byte length of the base64-encoded descriptor

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer parses file with explicit format argument
    Given a valid OpenAPI 3.1 YAML file exists at "spec.txt"
    When the developer runs parse command with file "spec.txt" and format "openapi_3_1"
    Then the command outputs JSON to stdout
    And the JSON field "format" matches the detected OpenAPI version from file content
    And the JSON field "endpoint_id" is null
    And the JSON field "source" is "file"

  @data-domain:migration-drift-gate
  Scenario: Developer attempts to parse file with unrecognized extension and no format
    Given a file exists at "schema.txt"
    When the developer runs parse command with file "schema.txt" and no format argument
    Then the command raises a ClickException mentioning inability to infer format

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Developer parses JSON file with array root element
    Given a file exists at "schema.json"
    And the JSON root element is an array
    When the developer runs parse command with file "schema.json" and no format argument
    Then the command raises a SchemaParseError

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer attempts to parse nonexistent file
    Given no file exists at "missing.yaml"
    When the developer runs parse command with file "missing.yaml"
    Then the command raises a file-not-found exception before format processing

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: Developer parses Proto3 file with syntax error
    Given a Proto3 file exists at "invalid.proto"
    And the Proto3 file contains syntax errors
    When the developer runs parse command with file "invalid.proto" and no format argument
    Then the command raises a RuntimeError with protoc error message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer parses OpenAPI file where detected version differs from inferred
    Given a YAML file exists at "spec.yaml"
    And the file content specifies OpenAPI version "3.0.0"
    When the developer runs parse command with file "spec.yaml" and no format argument
    Then the command outputs JSON to stdout
    And the JSON field "format" is "openapi_3_0"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Developer parses files with various extension-to-format mappings
    Given a valid <schema_type> file exists at "<filename>"
    When the developer runs parse command with file "<filename>" and no format argument
    Then the command outputs JSON to stdout
    And the JSON field "format" is "<expected_format>"
    And the JSON field "endpoint_id" is null
    And the JSON field "source" is "file"

    Examples:
      | schema_type   | filename      | expected_format       |
      | OpenAPI 3.1   | spec.yml      | openapi_3_1           |
      | JSON Schema   | data.json     | json_schema_2020_12   |
      | Proto3        | api.proto     | proto3                |
```
