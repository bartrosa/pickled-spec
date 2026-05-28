Feature: Schema Ambiguity Gate
  As a schema validation pipeline orchestrator
  I want to detect ambiguities between Gherkin specifications and schema YAML
  So that unclear or inconsistent schema mappings are flagged for review

  Background:
    Given a SchemaAmbiguityGate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when target is not a SchemaArtifact
    Given a target that is not a SchemaArtifact instance
    And a context with valid "gherkin_context"
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate a type mismatch with the received type

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when context is None
    Given a SchemaArtifact target
    And a context that is None
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate that "gherkin_context" is required

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when context lacks "gherkin_context" key
    Given a SchemaArtifact target
    And a context dictionary without "gherkin_context" key
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate that "gherkin_context" is missing

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Gate fails when "gherkin_context" is invalid string
    Given a SchemaArtifact target
    And a context with "gherkin_context" set to <invalid_value>
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate that "gherkin_context" must be a non-empty string

    Examples:
      | invalid_value      |
      | empty string       |
      | whitespace string  |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when "gherkin_context" is not a string type
    Given a SchemaArtifact target
    And a context with "gherkin_context" set to a non-string value
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate that "gherkin_context" must be a string

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate fails when LLM returns invalid JSON
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns a response that is not valid JSON
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes state "LLM returned malformed JSON"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate fails when LLM returns malformed markdown fences
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns a response with unmatched or malformed markdown fences
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes state "LLM returned malformed JSON"

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate fails when parsed JSON lacks "ambiguities" key
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns valid JSON without "ambiguities" key
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate the missing "ambiguities" list field

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate fails when "ambiguities" value is not a list
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns valid JSON with "ambiguities" as a non-list type
    When the gate runs
    Then the gate returns a FAIL verdict
    And the notes indicate that "ambiguities" must be a list

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate passes when ambiguities list is empty
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns valid JSON with an empty "ambiguities" list
    When the gate runs
    Then the gate returns a PASS verdict
    And the notes state "No ambiguities reported."
    And no findings are attached

  @pickled-internal:core-llm-cache-default-on
  Scenario Outline: Gate warns when ambiguities are detected
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns valid JSON with <count> ambiguities in the list
    When the gate runs
    Then the gate returns a WARN verdict
    And the notes include the count of <count> ambiguities
    And the findings tuple contains <count> ambiguity items

    Examples:
      | count |
      | 1     |
      | 3     |

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate sends rendered prompt with gherkin context and schema YAML to LLM
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    When the gate runs
    Then the gate renders a prompt containing the Gherkin context
    And the prompt contains the schema YAML content from the target
    And the prompt is sent to the LLM completion function

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate instructs LLM to return only JSON without markdown or commentary
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    When the gate runs
    Then the gate sends a system instruction to the LLM
    And the instruction requires a single JSON object response
    And the instruction prohibits markdown fences and extra commentary

  @pickled-internal:core-llm-cache-default-on
  Scenario Outline: Gate parses LLM response with various JSON formats
    Given a SchemaArtifact target with schema YAML content
    And a context with valid "gherkin_context"
    And the LLM returns <response_format>
    When the gate runs
    Then the gate successfully parses the JSON response
    And extracts the "ambiguities" field

    Examples:
      | response_format                                    |
      | plain JSON without fences                          |
      | JSON wrapped in triple-backtick fences             |
      | JSON wrapped in fences with "json" label           |
