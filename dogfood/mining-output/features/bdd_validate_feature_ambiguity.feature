Feature: BDD Practitioner validates feature file for ambiguous step definitions

  As a BDD practitioner
  I want to validate Gherkin feature files for ambiguous step definitions
  So that I can catch ambiguity issues early before running tests

  Background:
    Given the ambiguity gate is available as an MCP tool

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: BDD practitioner validates a feature file with no ambiguities
    Given a valid Gherkin feature file with unambiguous steps
    When the practitioner validates the feature text for ambiguity
    Then the validation returns success
    And no ambiguities are detected

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: BDD practitioner detects ambiguous step definitions
    Given a valid Gherkin feature file with ambiguous step definitions
    When the practitioner validates the feature text for ambiguity
    Then the validation returns failure
    And the ambiguities are reported

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: BDD practitioner validates malformed Gherkin syntax
    Given a feature file with invalid Gherkin syntax
    When the practitioner validates the feature text for ambiguity
    Then the validation handles the syntax error appropriately
    And an appropriate error message is returned

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: BDD practitioner validates empty feature text
    Given an empty feature text parameter
    When the practitioner validates the feature text for ambiguity
    Then the validation handles the empty input appropriately
    And an appropriate error message is returned

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario: BDD practitioner uses ambiguity gate independently
    Given other validation gates are available in the system
    When the practitioner validates the feature text for ambiguity only
    Then only the ambiguity gate is invoked
    And the validation completes without requiring other gates

  @bdd-domain:draft-warnings-field-populated-on-failure
  Scenario: Test automation engineer integrates ambiguity gate in CI/CD pipeline
    Given a CI/CD pipeline with automated quality gates
    When the ambiguity gate is invoked as an MCP tool
    Then the gate executes within the pipeline context
    And the validation results are returned for pipeline decision-making

  @bdd-domain:draft-output-parses-via-pytest-bdd
  Scenario Outline: BDD practitioner validates various Gherkin structures
    Given a feature file with <structure_type>
    When the practitioner validates the feature text for ambiguity
    Then the validation processes the structure correctly
    And ambiguity detection results are returned for <structure_type>

    Examples:
      | structure_type           |
      | scenario outlines        |
      | data tables             |
      | doc strings             |
      | tagged scenarios        |
      | multiple scenarios      |
      | background steps        |
