Feature: Plan Command
  As an infrastructure engineer
  I want to execute Terraform plan and capture the output as JSON
  So that I can analyze infrastructure changes and feed them into validation gates

  Background:
    Given a Terraform configuration exists

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer generates a plan with valid Terraform directory and output path
    Given a valid Terraform directory path "tf_dir"
    And a valid output file path "output.json"
    When the infrastructure engineer executes the plan command with "tf_dir" and "output.json"
    Then terraform plan is executed in the "tf_dir" directory
    And the plan output is captured in JSON format
    And the JSON data is written to "output.json"
    And the command exits with a success status code

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer generates a plan when output file does not exist
    Given a valid Terraform directory path "tf_dir"
    And an output file path "new_output.json" that does not exist
    When the infrastructure engineer executes the plan command with "tf_dir" and "new_output.json"
    Then the output file "new_output.json" is created
    And the JSON-formatted plan data is written to "new_output.json"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer generates a plan that produces valid JSON output
    Given a valid Terraform directory path "tf_dir"
    And a valid output file path "output.json"
    When the infrastructure engineer executes the plan command with "tf_dir" and "output.json"
    Then the generated output at "output.json" is valid JSON
    And the JSON output is parseable

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer generates a plan output consumable by validation gates
    Given a valid Terraform directory path "tf_dir"
    And a valid output file path "output.json"
    When the infrastructure engineer executes the plan command with "tf_dir" and "output.json"
    Then the JSON output can be consumed by IaCAmbiguityGate
    And the JSON output can be consumed by PlanDiffGate
    And the JSON output can be consumed by SecurityBaselineGate

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer attempts to generate a plan when terraform plan fails
    Given a valid Terraform directory path "tf_dir"
    And a valid output file path "output.json"
    And the Terraform configuration in "tf_dir" will cause plan to fail
    When the infrastructure engineer executes the plan command with "tf_dir" and "output.json"
    Then the command exits with a failure status code

  # TODO: Clarify expected behavior when tf_dir does not exist or is not a valid Terraform directory
  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario Outline: Infrastructure engineer provides invalid arguments
    Given an argument configuration with <tf_dir_state> and <output_state>
    When the infrastructure engineer executes the plan command
    Then the command exits with a failure status code

    Examples:
      | tf_dir_state | output_state |
      | missing      | valid        |
      | valid        | missing      |
      | missing      | missing      |
