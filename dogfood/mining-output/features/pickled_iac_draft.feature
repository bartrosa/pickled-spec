Feature: Draft Terraform module from natural-language user story

  As a user of the pickled-iac CLI
  I want to generate Terraform infrastructure code from a natural-language description
  So that I can define infrastructure without manually writing HCL

  Background:
    Given terraform or opentofu is available on the system PATH
    And the LLM client is properly configured

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User drafts a module and prints to stdout
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the user does not specify an output path
    When the draft command is invoked
    Then the generated HCL content is printed to stdout
    And no files are created on the file system

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User drafts a module and writes to a specified directory
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the user specifies an output path "/tmp/my-module"
    When the draft command is invoked
    Then the directory "/tmp/my-module" is created including any parent directories
    And a file named "main.tf" is written to "/tmp/my-module" containing the generated HCL
    And a confirmation message "Wrote /tmp/my-module/main.tf" is printed to stderr

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User drafts a module and writes to an existing directory
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "azure"
    And the directory "/tmp/existing-module" already exists
    When the draft command is invoked
    Then a file named "main.tf" is written to "/tmp/existing-module" containing the generated HCL
    And a confirmation message "Wrote /tmp/existing-module/main.tf" is printed to stderr

  @best-practices:agent-path-first-class
  Scenario: User drafts a module but neither terraform nor opentofu is available
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And neither terraform nor opentofu is available on the system PATH
    When the draft command is invoked
    Then an IaCToolMissingError is raised

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: User drafts a module with malformed custom LLM factory environment variable
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the environment variable PICKLED_IAC_LLM_FACTORY is set to "mypackage_get_client" without a colon separator
    When the draft command is invoked
    Then a ClickException is raised indicating the required "module:callable" format

  @pickled-internal:core-llm-cache-default-on
  Scenario: User drafts a module but LLM configuration is invalid
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the environment variable PICKLED_IAC_LLM_FACTORY is not set
    And the LLM configuration cannot be loaded
    When the draft command is invoked
    Then a ClickException is raised wrapping the underlying ConfigError

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM generates valid HCL on first attempt
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the LLM generates valid HCL on the first attempt
    When the draft command is invoked
    Then terraform validate or opentofu validate is executed against the generated HCL
    And the validation succeeds
    And the validated HCL is returned

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM generates invalid HCL but succeeds on retry
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the LLM generates invalid HCL on the first attempt
    And the LLM generates valid HCL on the second attempt
    When the draft command is invoked
    Then terraform validate or opentofu validate is executed against the first generated HCL
    And the validation fails with diagnostic messages
    And the LLM is called again with the user story and the validation error feedback
    And terraform validate or opentofu validate is executed against the second generated HCL
    And the validation succeeds
    And the validated HCL is returned

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM fails to generate valid HCL after 3 attempts
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the LLM generates invalid HCL on all 3 attempts
    When the draft command is invoked
    Then terraform validate or opentofu validate is executed 3 times
    And each validation fails with diagnostic messages
    And an IaCValidationError is raised containing all collected validation diagnostics

  @pickled-internal:core-llm-cache-default-on
  Scenario: LLM response contains code fences which are stripped
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the LLM response includes leading and trailing triple-backtick fences
    When the draft command is invoked
    Then the code fences are stripped from the LLM response
    And terraform validate or opentofu validate is executed against the stripped HCL
    And the validation succeeds

  @bdd-domain:draft-empty-story-deterministic-failure
  Scenario Outline: User specifies different cloud providers
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "<provider>"
    When the draft command is invoked
    Then the provider "<provider>" is passed to the prompt rendering
    And the generated HCL contains resources specific to "<provider>"

    Examples:
      | provider |
      | aws      |
      | azure    |
      | gcp      |

  @pickled-internal:mcp-subserver-llm-client-wired
  Scenario: User invokes draft with custom LLM factory
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the environment variable PICKLED_IAC_LLM_FACTORY is set to "mypackage:get_client"
    When the draft command is invoked
    Then the module "mypackage" is dynamically imported
    And the callable "get_client" is invoked to obtain the LLM client
    And the custom LLM client is used for generation

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User invokes draft without custom factory and PICKLED_LLM_PROVIDER not set
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the environment variable PICKLED_IAC_LLM_FACTORY is not set
    And the environment variable PICKLED_LLM_PROVIDER is not set
    When the draft command is invoked
    Then the LLM provider defaults to "anthropic"
    And the LLM client is built using pickled_core.llm.factory.build_client
    And the LLM configuration is loaded from pickled_core.llm.config.load_config

  @pickled-internal:core-llm-cache-default-on
  Scenario: Validation process initializes terraform directory
    Given the user provides a user story describing desired infrastructure
    And the user specifies a provider "aws"
    And the LLM generates valid HCL
    When the draft command is invoked
    Then the generated HCL is written to a temporary directory
    And terraform init or opentofu init is run if needed
    And terraform validate or opentofu validate is executed in JSON mode
    And the validation succeeds
