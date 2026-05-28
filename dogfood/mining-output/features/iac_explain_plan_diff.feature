Feature: IaC Explain Plan Diff Tool
  As an infrastructure engineer
  I want to analyze Terraform plan changes for risk
  So that I can understand the impact before applying changes

  Background:
    Given the IaC Explain Plan Diff tool is available

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer requests analysis of a valid Terraform plan
    Given a valid Terraform plan JSON file
    When the plan is submitted to the iac_explain_plan_diff tool
    Then a summary of the plan changes is returned
    And the summary identifies any risky actions

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer receives ambiguous configuration warnings
    Given a valid Terraform plan JSON file with ambiguous configurations
    When the plan is submitted to the iac_explain_plan_diff tool
    Then the IaCAmbiguityGate is invoked to detect ambiguous configurations
    And the summary includes ambiguous configuration risks

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer receives plan difference analysis
    Given a valid Terraform plan JSON file with significant differences
    When the plan is submitted to the iac_explain_plan_diff tool
    Then the PlanDiffGate is invoked to analyze plan differences
    And the summary includes plan difference risks

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer receives security baseline violations
    Given a valid Terraform plan JSON file with security baseline violations
    When the plan is submitted to the iac_explain_plan_diff tool
    Then the SecurityBaselineGate is invoked to check security policy violations
    And the summary includes security baseline risks

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer analyzes a plan with multiple risk types
    Given a valid Terraform plan JSON file with multiple risk categories
    When the plan is submitted to the iac_explain_plan_diff tool
    Then all applicable gates are executed
    And the summary distinguishes between ambiguous configuration risks
    And the summary distinguishes between plan difference risks
    And the summary distinguishes between security baseline risks

  # TODO: Clarify expected error message format and structure
  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer submits malformed Terraform plan JSON
    Given a malformed Terraform plan JSON file
    When the plan is submitted to the iac_explain_plan_diff tool
    Then an error is returned indicating invalid JSON

  # TODO: Clarify expected error message format and structure
  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer submits invalid Terraform plan structure
    Given a JSON file that is not a valid Terraform plan structure
    When the plan is submitted to the iac_explain_plan_diff tool
    Then an error is returned indicating invalid plan structure

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Infrastructure engineer omits required plan_json parameter
    When the iac_explain_plan_diff tool is invoked without the plan_json parameter
    Then an error is returned indicating the parameter is required

  @iac-domain:terraform-validate-entry
  Scenario: Infrastructure engineer analyzes a plan with no risks
    Given a valid Terraform plan JSON file with no risky actions
    When the plan is submitted to the iac_explain_plan_diff tool
    Then a summary is returned
    And the summary indicates no risks were identified
