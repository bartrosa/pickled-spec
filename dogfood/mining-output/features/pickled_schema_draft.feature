Feature: Draft OpenAPI path item from Gherkin scenario
  As a developer
  I want to generate OpenAPI 3.1 path item specifications from Gherkin scenarios
  So that I can automate API documentation from BDD scenarios

  Background:
    Given a valid Gherkin scenario file exists

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer drafts path item to stdout
    Given the output parameter is not specified
    When the draft command is executed with method "GET" and endpoint "/users"
    Then valid OpenAPI path item YAML is printed to stdout
    And the YAML is formatted with sort_keys set to false
    And the YAML is formatted with default_flow_style set to false

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer drafts path item to file
    Given the output parameter specifies a file path
    When the draft command is executed with method "POST" and endpoint "/users"
    Then the OpenAPI path item YAML is written to the specified file as UTF-8
    And a confirmation message "Wrote {output}" is printed to stderr

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer uses custom LLM factory via environment variable
    Given the PICKLED_SCHEMA_LLM_FACTORY environment variable is set to "mymodule:my_factory"
    When the draft command is executed
    Then the command imports "mymodule" and invokes "my_factory"
    And the factory result is used as the LLM client

  @pickled-internal:core-llm-cache-default-on
  Scenario: Developer provides malformed LLM factory configuration
    Given the PICKLED_SCHEMA_LLM_FACTORY environment variable is set to "mymodule_no_colon"
    When the draft command is executed
    Then a ClickException is raised about the required format

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer uses default LLM provider
    Given the PICKLED_SCHEMA_LLM_FACTORY environment variable is not set
    And the PICKLED_LLM_PROVIDER environment variable is not set
    When the draft command is executed
    Then the command uses "anthropic" as the default provider
    And pickled_core's build_client is invoked with loaded configuration

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: Developer specifies custom LLM provider
    Given the PICKLED_SCHEMA_LLM_FACTORY environment variable is not set
    And the PICKLED_LLM_PROVIDER environment variable is set to "openai"
    When the draft command is executed
    Then the command uses "openai" as the provider
    And pickled_core's build_client is invoked with loaded configuration

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM client configuration fails
    Given the PICKLED_SCHEMA_LLM_FACTORY environment variable is not set
    When pickled_core's build_client raises a ConfigError
    Then a ClickException is raised with the configuration error details

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM produces valid OpenAPI on first attempt
    Given the LLM client is configured
    When the LLM returns valid OpenAPI path item YAML
    Then the YAML is validated against OpenAPI 3.1.0 specification
    And the validated YAML is returned as output
    And no retry attempts are made

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM produces invalid YAML and succeeds on retry
    Given the LLM client is configured
    When the LLM returns invalid YAML on the first attempt
    And the LLM returns valid OpenAPI path item YAML on the second attempt
    Then the command retries with validation feedback in the prompt
    And the validated YAML from the second attempt is returned as output

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM produces non-mapping YAML output
    Given the LLM client is configured
    When the LLM returns YAML that is not a dictionary on all attempts
    Then a SchemaValidationError is raised about expecting a mapping

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM produces output failing OpenAPI validation
    Given the LLM client is configured
    When the LLM returns output that fails OpenAPI validation on the first attempt
    Then the second prompt includes the previous validation error
    And the command retries up to 3 times total

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: All validation attempts fail
    Given the LLM client is configured
    When the LLM produces invalid output on all 3 attempts
    Then a SchemaValidationError is raised with the last failure details

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: OpenAPI validator is not installed
    Given the pickled-schema[openapi] extra is not installed
    When the draft command attempts validation
    Then a SchemaValidationError is raised requesting pickled-schema[openapi]

  Scenario: Method parameter is uppercased for prompts
    Given the method parameter is "get"
    When the prompt template is rendered
    Then the method is uppercased to "GET" in the prompt
    And the method is uppercased in the endpoint_id

  @schema-domain:openapi-validate-deterministic
  Scenario: Method parameter is lowercased for validation
    Given the method parameter is "GET"
    When the validation envelope is constructed
    Then the method is lowercased to "get" in the OpenAPI paths object

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM returns bare operation object
    Given the LLM client is configured
    When the LLM returns a dictionary without a path wrapper
    And the dictionary contains operation properties
    Then the operation is unwrapped and used as the path item
    And the path item is validated successfully

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: LLM returns operation wrapped with HTTP method key
    Given the LLM client is configured
    When the LLM returns a single-key dictionary with the HTTP method
    And the value contains operation properties
    Then the operation is unwrapped from the method key
    And the path item is validated successfully

  @best-practices:agent-path-first-class
  Scenario: Gherkin file cannot be read
    Given the gherkin_file parameter specifies a non-existent path
    When the draft command is executed
    Then a file I/O error is raised

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Output file cannot be written
    Given the output parameter specifies a write-protected path
    When the draft command attempts to write the YAML
    Then a file I/O error is raised
