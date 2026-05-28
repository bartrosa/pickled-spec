Feature: BDD Draft Feature from Story Tool

  As a BDD practitioner
  I want to generate a first-draft Gherkin feature file from a natural-language user story
  So that I can accelerate the transition from informal requirements to structured specifications

  Background:
    Given the bdd_draft_feature_from_story tool is available

  @bdd-domain:gherkin-feature-header-required
  Scenario: Practitioner generates feature from simple user story
    Given a simple user story text
    When the practitioner invokes the tool with the story text
    Then a response containing valid Gherkin keywords is returned
    And the response includes a Feature declaration
    And the response includes at least one Scenario
    And the response includes Given, When, and Then steps

  @bdd-domain:gherkin-feature-header-required
  Scenario: Practitioner saves generated feature to file
    Given a user story text
    And the practitioner has invoked the tool with the story text
    When the generated output is written to a .feature file
    Then the file is created without syntax errors
    And the file contains valid Gherkin structure

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Practitioner generates feature with empty story text
    Given an empty story text
    When the practitioner invokes the tool with the story text
    Then either an error is returned or a minimal valid feature template is produced

  @bdd-domain:gherkin-feature-header-required
  Scenario: Practitioner generates feature with whitespace-only story text
    Given a story text containing only whitespace
    When the practitioner invokes the tool with the story text
    Then either an error is returned or a minimal valid feature template is produced

  # TODO: Verify exact instrumentation approach for observing gate invocation
  @bdd-domain:gherkin-feature-header-required
  Scenario: Tool invokes ambiguity gate during processing
    Given a user story text
    When the practitioner invokes the tool with the story text
    Then the AmbiguityGate.run method is invoked before feature generation
    And gate execution is observable via instrumentation or logs

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: Gate failure prevents feature generation
    Given a user story text that triggers gate failure
    When the practitioner invokes the tool with the story text
    Then feature generation is prevented
    And an appropriate error message is returned
    And no feature content is produced

  @bdd-domain:gherkin-feature-header-required
  Scenario: Generated feature incorporates input story elements
    Given a user story text with specific requirements and acceptance criteria
    When the practitioner invokes the tool with the story text
    Then the generated feature references elements from the input story
    And the feature content is derived from the story requirements

  @bdd-domain:gherkin-feature-header-required
  Scenario: Multiple invocations produce consistent output
    Given a user story text
    When the practitioner invokes the tool multiple times with the same story text
    Then each invocation produces output with consistent structure
    And the Feature and Scenario organization remains stable across invocations
