Feature: Infrastructure-as-Code validation orchestration
  As a CI/CD pipeline
  I want to validate Terraform/OpenTofu configurations and scan for security issues
  So that I can prevent misconfigured or insecure infrastructure from being deployed

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation when infra directory is missing
    Given the workdir does not contain an "infra/" subdirectory
    When the user runs the IaC validation gate
    Then the gate returns a single GateResult
    And the result has gate_name "iac.infra"
    And the result has verdict "WARN"
    And the result notes contain "no infra/ directory"

  @iac-domain:terraform-validate-entry
  Scenario: User runs validation when Terraform/OpenTofu binary is not on PATH
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is not found on PATH
    When the user runs the IaC validation gate
    Then the gate returns 2 GateResult objects
    And the "iac.validate" result has verdict "WARN"
    And the "iac.validate" result notes contain the IaCToolMissingError message

  @iac-domain:terraform-validate-entry
  Scenario: User runs validation when Terraform configuration is valid
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is found on PATH
    And the Terraform directory is initialized
    And the Terraform configuration is valid
    When the user runs the IaC validation gate
    Then the "iac.validate" result has verdict "PASS"
    And the "iac.validate" result notes contain "ok" or validation diagnostics

  @iac-domain:terraform-validate-entry
  Scenario: User runs validation when Terraform configuration is invalid
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is found on PATH
    And the Terraform directory is initialized
    And the Terraform configuration reports valid=false
    When the user runs the IaC validation gate
    Then the "iac.validate" result has verdict "FAIL"
    And the "iac.validate" result notes contain semicolon-separated diagnostic messages

  @iac-domain:terraform-validate-entry
  Scenario: User runs validation when Terraform validate raises unexpected exception
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is found on PATH
    And the Terraform validation raises an unexpected exception
    When the user runs the IaC validation gate
    Then the "iac.validate" result has verdict "FAIL"
    And the "iac.validate" result notes contain the exception message

  @iac-domain:terraform-validate-entry
  Scenario: User runs validation and Terraform directory requires initialization
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is found on PATH
    And the ".terraform/" directory does not exist in "infra/"
    When the user runs the IaC validation gate
    Then the gate executes "terraform init -input=false -backend=false"
    And the terraform init uses environment variable TF_IN_AUTOMATION=1
    And the terraform validate runs after successful initialization

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation when Trivy binary is not on PATH
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is not found on PATH
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "PASS"
    And the security baseline result notes contain "trivy not found on PATH — security scan skipped"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation when Trivy finds CRITICAL severity misconfigurations
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is found on PATH
    And Trivy scan detects CRITICAL severity misconfigurations
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "FAIL"
    And the security baseline result includes findings tuple with CRITICAL issue titles

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User runs validation when Trivy finds HIGH severity misconfigurations only
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is found on PATH
    And Trivy scan detects HIGH severity misconfigurations
    And Trivy scan detects no CRITICAL severity misconfigurations
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "WARN"
    And the security baseline result includes findings tuple with HIGH issue titles

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation when Trivy finds no HIGH or CRITICAL misconfigurations
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is found on PATH
    And Trivy scan detects no HIGH or CRITICAL severity misconfigurations
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "PASS"
    And the security baseline result notes contain "No HIGH or CRITICAL findings."

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User runs validation when Trivy returns non-JSON output
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is found on PATH
    And Trivy returns non-JSON output
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "WARN"
    And the security baseline result notes contain "trivy returned non-JSON output"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation when Trivy execution fails with unexpected error
    Given the workdir contains an "infra/" subdirectory
    And the Trivy binary is found on PATH
    And Trivy execution fails with a non-0/1 return code and no stdout
    When the user runs the IaC validation gate
    Then the security baseline result has verdict "WARN"
    And the security baseline result notes contain error details

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation and receives expected result structure
    Given the workdir contains an "infra/" subdirectory
    When the user runs the IaC validation gate
    Then the gate returns a list of GateResult objects
    And the list contains 2 GateResult objects
    And each GateResult has gate_name, verdict, and notes attributes
    And the list is never None or a single GateResult object

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs validation with all Terraform subprocess calls
    Given the workdir contains an "infra/" subdirectory
    And the Terraform/OpenTofu binary is found on PATH
    When the user runs the IaC validation gate
    Then all Terraform/OpenTofu subprocess calls include environment variable TF_IN_AUTOMATION=1
