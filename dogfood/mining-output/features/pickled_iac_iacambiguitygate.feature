```gherkin
Feature: IaC Ambiguity Gate Evaluation
  As a DevOps engineer
  I want to validate Terraform artifacts against user stories for ambiguities
  So that I can identify potential implementation issues before deployment

  Background:
    Given an IaC ambiguity gate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects non-IaCArtifact target
    When the gate runs with a target that is not an IaCArtifact instance
    Then the gate returns a FAIL verdict
    And the result note indicates the actual type received
    And the result includes the gate name

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects missing user story when context is None
    Given a valid IaCArtifact target
    When the gate runs with context set to None
    Then the gate returns a FAIL verdict
    And the result note states the user story requirement
    And the result includes the gate name

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects non-string user story
    Given a valid IaCArtifact target
    When the gate runs with context containing a non-string "user_story" value
    Then the gate returns a FAIL verdict
    And the result note states the user story requirement
    And the result includes the gate name

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Gate rejects empty or whitespace-only user story
    Given a valid IaCArtifact target
    When the gate runs with context containing user story "<user_story>"
    Then the gate returns a FAIL verdict
    And the result note states the user story requirement
    And the result includes the gate name

    Examples:
      | user_story |
      |            |
      |            |
      |    	     |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate renders template with user story and artifact content
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    When the gate runs
    Then the gate renders the template with the user story
    And the gate renders the template with the target content

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate calls LLM with JSON-only system message
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    When the gate runs
    Then the gate calls complete_prompt with a system message requesting JSON without markdown

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate rejects unparseable LLM response
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns a response that cannot be parsed as JSON
    When the gate runs
    Then the gate returns a FAIL verdict
    And the result note is "LLM returned malformed JSON"
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate rejects non-dictionary JSON response
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns a JSON array
    When the gate runs
    Then the gate returns a FAIL verdict
    And the result note is "LLM returned malformed JSON"
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate rejects JSON missing ambiguities key
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns JSON without an "ambiguities" key
    When the gate runs
    Then the gate returns a FAIL verdict
    And the result note is "LLM JSON missing list field \"ambiguities\""
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate rejects JSON with non-list ambiguities value
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns JSON with "ambiguities" as a non-list value
    When the gate runs
    Then the gate returns a FAIL verdict
    And the result note is "LLM JSON missing list field \"ambiguities\""
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate passes when no ambiguities reported
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns JSON with an empty "ambiguities" list
    When the gate runs
    Then the gate returns a PASS verdict
    And the result note is "No ambiguities reported."
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate warns when ambiguities are detected
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns JSON with 3 items in the "ambiguities" list
    When the gate runs
    Then the gate returns a WARN verdict
    And the result note indicates 3 ambiguities
    And the result findings contain the ambiguities as a tuple
    And the result includes the gate name

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate extracts JSON from markdown code fences
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns valid JSON wrapped in markdown code fences starting with "```"
    When the gate runs
    Then the gate extracts content between the first and last "```" delimiters
    And the gate parses the extracted JSON successfully

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate extracts JSON between first and last braces
    Given a valid IaCArtifact target with content
    And a context with a valid user story
    And the LLM returns a response with extra text before and after JSON
    When the gate runs
    Then the gate extracts the substring between the first "{" and last "}"
    And the gate parses the extracted JSON successfully
```
