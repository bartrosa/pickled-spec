Feature: Validate Terraform directory
  As an AI agent or automation workflow
  I want to validate Terraform configuration files in a temporary directory
  So that I can verify syntax and structure before planning or deployment

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates syntactically correct Terraform files
    Given a temporary directory contains valid Terraform configuration files
    When the agent invokes the validate tool with the tf_files parameter
    Then the validation returns a success result
    And the result indicates all configurations are valid

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates Terraform files with syntax errors
    Given a temporary directory contains Terraform files with syntax errors
    When the agent invokes the validate tool with the tf_files parameter
    Then the validation returns a failure result
    And the result identifies the syntax errors

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates multiple Terraform files in one invocation
    Given a temporary directory contains multiple valid Terraform configuration files
    When the agent invokes the validate tool with all files in the tf_files parameter
    Then the validation processes all files
    And the validation returns a success result for the entire set

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates mixed valid and invalid Terraform files
    Given a temporary directory contains both valid and invalid Terraform files
    When the agent invokes the validate tool with the tf_files parameter
    Then the validation processes all files
    And the validation returns a failure result
    And the result distinguishes between files with errors and valid files

  @iac-domain:terraform-validate-entry
  Scenario: Agent attempts validation without required tf_files parameter
    When the agent invokes the validate tool without the tf_files parameter
    Then the validation returns an error
    And the error indicates the tf_files parameter is required

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates Terraform files with structural issues
    Given a temporary directory contains Terraform files with structural validity issues
    When the agent invokes the validate tool with the tf_files parameter
    Then the validation returns a failure result
    And the result identifies the structural issues

  @iac-domain:terraform-validate-entry
  Scenario: Agent validates empty Terraform configuration
    Given a temporary directory contains an empty Terraform configuration file
    When the agent invokes the validate tool with the tf_files parameter
    Then the validation processes the file
    And the validation returns a result indicating the configuration state
