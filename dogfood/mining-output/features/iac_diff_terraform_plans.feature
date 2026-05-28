Feature: IaC Diff Terraform Plans Tool

  As an automation workflow or CI/CD pipeline
  I want to analyze infrastructure changes between two Terraform plan states
  So that I can validate changes before applying them to environments

  Background:
    Given the iac_diff_terraform_plans MCP tool is available

  @iac-domain:terraform-validate-entry
  Scenario: Automation workflow compares valid base and head Terraform plans
    Given a valid Terraform plan JSON for the base state
    And a valid Terraform plan JSON for the head state
    When the workflow calls iac_diff_terraform_plans with base_plan_json and head_plan_json
    Then a comparison result structure is returned
    And the result shows resources to be added
    And the result shows resources to be modified
    And the result shows resources to be destroyed

  @iac-domain:terraform-validate-entry
  Scenario: Automation workflow provides base plan as current state and head plan as proposed changes
    Given base_plan_json represents the current infrastructure state
    And head_plan_json represents proposed infrastructure changes
    When the workflow calls iac_diff_terraform_plans with base_plan_json and head_plan_json
    Then the comparison result reflects differences between current and proposed states

  # TODO: Define valid Terraform plan JSON format specification
  @iac-domain:terraform-validate-entry
  Scenario Outline: Tool rejects invalid Terraform plan JSON formats
    Given <invalid_input> is not valid Terraform plan JSON format
    When the workflow calls iac_diff_terraform_plans with the invalid input as <argument>
    Then an error is returned indicating invalid JSON format for <argument>

    Examples:
      | invalid_input      | argument        |
      | malformed JSON     | base_plan_json  |
      | empty string       | base_plan_json  |
      | non-JSON text      | base_plan_json  |
      | malformed JSON     | head_plan_json  |
      | empty string       | head_plan_json  |
      | non-JSON text      | head_plan_json  |

  @iac-domain:terraform-validate-entry
  Scenario: Tool is called without required base_plan_json argument
    Given head_plan_json is provided
    When the workflow calls iac_diff_terraform_plans without base_plan_json
    Then an error is returned indicating base_plan_json is required

  @iac-domain:terraform-validate-entry
  Scenario: Tool is called without required head_plan_json argument
    Given base_plan_json is provided
    When the workflow calls iac_diff_terraform_plans without head_plan_json
    Then an error is returned indicating head_plan_json is required

  @iac-domain:terraform-validate-entry
  Scenario: IaCAmbiguityGate consumes comparison result output
    Given iac_diff_terraform_plans has produced a comparison result
    When IaCAmbiguityGate.run processes the comparison result
    Then the gate successfully consumes the output structure

  @iac-domain:terraform-validate-entry
  Scenario: PlanDiffGate consumes comparison result output
    Given iac_diff_terraform_plans has produced a comparison result
    When PlanDiffGate.run processes the comparison result
    Then the gate successfully consumes the output structure

  @iac-domain:terraform-validate-entry
  Scenario: SecurityBaselineGate consumes comparison result output
    Given iac_diff_terraform_plans has produced a comparison result
    When SecurityBaselineGate.run processes the comparison result
    Then the gate successfully consumes the output structure

  @iac-domain:terraform-validate-entry
  Scenario: run_all gate operation consumes comparison result output
    Given iac_diff_terraform_plans has produced a comparison result
    When run_all gate operation processes the comparison result
    Then all gates successfully consume the output structure
