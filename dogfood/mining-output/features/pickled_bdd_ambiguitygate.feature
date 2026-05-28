Feature: AmbiguityGate analyzes BDD scenarios for ambiguity

  As a quality engineer
  I want to check feature scenarios for ambiguous wording
  So that implementation teams receive unambiguous requirements

  Background:
    Given an AmbiguityGate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Quality engineer runs gate against a non-Feature object
    When the engineer runs the gate with a target of type "dict"
    Then the gate returns verdict FAIL
    And the notes describe the type mismatch "Expected Feature, got dict"
    And the findings tuple is empty

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Quality engineer runs gate against a Feature with zero scenarios
    Given a Feature with 0 scenarios
    When the engineer runs the gate
    Then the gate returns verdict PASS
    And the notes indicate "0/0 scenarios flagged ambiguous"
    And the findings tuple is empty

  @pickled-internal:core-llm-cache-default-on
  Scenario: Quality engineer runs gate against unambiguous scenarios
    Given a Feature with 3 scenarios
    And the LLM identifies 0 scenarios as ambiguous
    When the engineer runs the gate
    Then the gate returns verdict PASS
    And the notes indicate "0/3 scenarios flagged ambiguous"
    And the findings tuple is empty

  @pickled-internal:core-llm-cache-default-on
  Scenario: Quality engineer runs gate against fully ambiguous scenarios
    Given a Feature with 3 scenarios
    And the LLM identifies 3 scenarios as ambiguous
    When the engineer runs the gate
    Then the gate returns verdict FAIL
    And the notes indicate "3/3 scenarios flagged ambiguous"
    And the findings tuple contains 3 AmbiguityFinding objects

  @pickled-internal:core-llm-cache-default-on
  Scenario: Quality engineer runs gate against partially ambiguous scenarios
    Given a Feature with 4 scenarios
    And the LLM identifies 2 scenarios as ambiguous
    When the engineer runs the gate
    Then the gate returns verdict WARN
    And the notes indicate "2/4 scenarios flagged ambiguous"
    And the findings tuple contains 2 AmbiguityFinding objects

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Quality engineer runs gate when all LLM responses fail to parse
    Given a Feature with 3 scenarios
    And all LLM responses return malformed JSON
    When the engineer runs the gate
    Then the gate returns verdict WARN
    And the findings tuple is empty
    And the notes list all 3 scenario names as parse errors

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Quality engineer runs gate when some responses fail to parse and rest are unambiguous
    Given a Feature with 4 scenarios
    And 2 LLM responses return malformed JSON
    And the LLM identifies 0 of the remaining scenarios as ambiguous
    When the engineer runs the gate
    Then the gate returns verdict WARN
    And the findings tuple is empty
    And the notes indicate "0/2 scenarios flagged ambiguous"
    And the notes list 2 scenario names as parse errors

  @pickled-internal:core-llm-cache-default-on
  Scenario: Quality engineer runs gate when some responses fail to parse and rest are ambiguous
    Given a Feature with 4 scenarios
    And 1 LLM response returns malformed JSON
    And the LLM identifies 2 of the remaining 3 scenarios as ambiguous
    When the engineer runs the gate
    Then the gate returns verdict WARN
    And the findings tuple contains 2 AmbiguityFinding objects
    And the notes indicate "2/3 scenarios flagged ambiguous"
    And the notes list 1 scenario name as parse error

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Quality engineer examines an AmbiguityFinding
    Given a Feature with 1 scenario named "User logs in"
    And the LLM identifies the scenario as ambiguous with 2 alternatives and a suggested fix
    When the engineer runs the gate
    Then the first finding contains scenario name "User logs in"
    And the first finding contains a tuple of 2 alternative implementation strings
    And the first finding contains a suggested fix string

  @pickled-internal:core-llm-cache-default-on
  Scenario Outline: Quality engineer runs gate against LLM responses with markdown fences
    Given a Feature with 1 scenario
    And the LLM response contains <fence_style>
    And the enclosed JSON indicates the scenario is <ambiguity_status>
    When the engineer runs the gate
    Then the gate successfully parses the JSON
    And the gate returns verdict <expected_verdict>

    Examples:
      | fence_style                          | ambiguity_status | expected_verdict |
      | triple backticks without language    | ambiguous        | FAIL             |
      | triple backticks with "json" tag     | ambiguous        | FAIL             |
      | triple backticks without language    | unambiguous      | PASS             |
      | triple backticks with "json" tag     | unambiguous      | PASS             |

  @pickled-internal:core-llm-cache-default-on
  Scenario: Quality engineer provides context parameter
    Given a Feature with 2 scenarios
    And the LLM identifies 0 scenarios as ambiguous
    And a context dictionary with arbitrary keys
    When the engineer runs the gate with the context parameter
    Then the gate returns verdict PASS
    And the result is identical to running without context
