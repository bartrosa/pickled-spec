Feature: Validate Terraform configuration via CLI command
  As a CLI user
  I want to run terraform validate on a specified directory
  So that I can verify my Terraform configurations are syntactically valid and internally consistent

  @iac-domain:terraform-validate-entry
  Scenario: User validates Terraform configuration in a valid directory
    Given a directory contains valid Terraform configuration files
    When the user invokes validate with that directory as tf_dir
    Then terraform validate executes on the specified directory
    And the validation result indicates success

  @iac-domain:terraform-validate-entry
  Scenario: User validates Terraform configuration with syntax errors
    Given a directory contains invalid Terraform configuration files
    When the user invokes validate with that directory as tf_dir
    Then terraform validate executes on the specified directory
    And the validation result indicates failure
    And validation errors are reported to the caller

  @iac-domain:terraform-validate-entry
  Scenario: User invokes validate without providing tf_dir parameter
    When the user invokes validate without the tf_dir parameter
    Then the command fails with an error
    And the error indicates tf_dir is required

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario: User invokes validate with empty tf_dir parameter
    When the user invokes validate with an empty tf_dir parameter
    Then the command fails with an error
    And the error indicates tf_dir is required

  @iac-domain:terraform-validate-entry
  Scenario: User validates specific directory different from current working directory
    Given the current working directory is "/workspace/project"
    And a directory "/workspace/terraform/modules/vpc" contains Terraform configuration files
    When the user invokes validate with "/workspace/terraform/modules/vpc" as tf_dir
    Then terraform validate executes on "/workspace/terraform/modules/vpc"
    And terraform validate does not execute on "/workspace/project"

  @iac-domain:terraform-validate-entry
  Scenario: Validation results are passed back to the caller
    Given a directory contains Terraform configuration files
    When the user invokes validate with that directory as tf_dir
    Then the command completes execution
    And the validation status is returned to the caller
    And the validation output is available to the caller
