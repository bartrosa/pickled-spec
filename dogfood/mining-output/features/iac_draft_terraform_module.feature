Feature: Infrastructure-as-code draft Terraform module generation
  As an infrastructure engineer or automation workflow
  I want to generate Terraform module drafts from natural-language user stories
  So that I can accelerate infrastructure provisioning and submit modules to validation gates

  @iac-domain:terraform-validate-entry
  Scenario: Engineer drafts a module with minimal user story
    Given a user story "Create an S3 bucket for application logs"
    When the engineer calls iac_draft_terraform_module with the user story
    Then a Terraform module draft is returned
    And the module contains valid Terraform syntax

  @iac-domain:terraform-validate-entry
  Scenario: Engineer drafts a module without specifying provider
    Given a user story "Deploy a virtual machine with 2 CPUs and 4GB RAM"
    When the engineer calls iac_draft_terraform_module with the user story
    And the provider parameter is omitted
    Then a Terraform module draft is returned with default provider configuration

  @iac-domain:terraform-validate-entry
  Scenario: Engineer drafts a module with explicit provider
    Given a user story "Create a storage account for blob data"
    And a provider "azure"
    When the engineer calls iac_draft_terraform_module with the user story and provider
    Then a Terraform module draft is returned
    And the module includes azure provider-specific resources

  @iac-domain:terraform-validate-entry
  Scenario: Tool rejects call missing required user story
    When the engineer calls iac_draft_terraform_module without a user story parameter
    Then the tool returns an error indicating the user_story parameter is required

  @iac-domain:terraform-validate-entry
  Scenario: Generated module conforms to Terraform structure
    Given a user story "Create a VPC with public and private subnets"
    When the engineer calls iac_draft_terraform_module with the user story
    Then the returned module contains resource blocks
    And the module contains variable definitions
    And the module contains output definitions
    And the module structure is valid for Terraform module consumption

  @iac-domain:terraform-validate-entry
  Scenario: Generated module can be consumed by IaCAmbiguityGate
    Given a user story "Deploy a load balancer"
    And a Terraform module draft generated from the user story
    When IaCAmbiguityGate.run is called with the generated module
    Then the gate processes the module without structural errors

  @iac-domain:terraform-validate-entry
  Scenario: Generated module can be consumed by PlanDiffGate
    Given a user story "Create a database instance"
    And a Terraform module draft generated from the user story
    When PlanDiffGate.run is called with the generated module
    Then the gate processes the module without structural errors

  @iac-domain:terraform-validate-entry
  Scenario: Generated module can be consumed by SecurityBaselineGate
    Given a user story "Provision compute resources"
    And a Terraform module draft generated from the user story
    When SecurityBaselineGate.run is called with the generated module
    Then the gate processes the module without structural errors

  @iac-domain:terraform-validate-entry
  Scenario: Generated module participates in run_all multi-gate workflow
    Given a user story "Deploy a web application infrastructure"
    And a Terraform module draft generated from the user story
    When run_all gate is invoked with the generated module
    Then the module passes through all configured gates in sequence
    And each gate receives the module in valid format

  @iac-domain:terraform-validate-entry
  Scenario Outline: Tool handles edge-case user stories gracefully
    Given a user story "<user_story_input>"
    When the engineer calls iac_draft_terraform_module with the user story
    Then the tool <outcome>

    Examples:
      | user_story_input | outcome |
      |                  | returns an error indicating user story cannot be empty |
      | A very long user story description that contains thousands of characters representing an extremely detailed infrastructure request with multiple components, dependencies, networking requirements, security policies, compliance rules, monitoring specifications, backup strategies, disaster recovery plans, scaling policies, cost optimization requirements, and various other infrastructure considerations that would typically span multiple pages of documentation | returns a Terraform module draft or gracefully handles length limits |
      | Create a bucket with name "special-chars-#$%&*@!" | returns a Terraform module draft handling special characters appropriately |

  @iac-domain:terraform-validate-entry
  Scenario Outline: Tool supports multiple cloud providers
    Given a user story "Create object storage"
    And a provider "<provider>"
    When the engineer calls iac_draft_terraform_module with the user story and provider
    Then a Terraform module draft is returned
    And the module uses <provider>-specific resource types

    Examples:
      | provider |
      | aws      |
      | azure    |
      | gcp      |
