Feature: Terraform security scanning CLI command
  As an operator or CI/CD pipeline
  I want to scan Terraform configurations for security issues
  So that I can prevent infrastructure deployments with critical vulnerabilities

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator scans when Trivy is not installed
    Given trivy is not available on PATH
    When the operator runs scan on a Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "PASS"
    And the JSON notes field indicates the security scan was skipped
    And the JSON findings field is an empty list
    And the command exits with code 0

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator provides invalid input type
    Given trivy is available on PATH
    When the operator runs scan with a non-Path argument
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "FAIL"
    And the JSON notes field mentions type mismatch
    And the JSON findings field is an empty list
    And the command exits with code 2

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator scans clean Terraform configuration
    Given trivy is available on PATH
    And the Terraform directory contains no HIGH or CRITICAL security issues
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "PASS"
    And the JSON notes field indicates no issues found
    And the JSON findings field is an empty list
    And the command exits with code 0

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator scans configuration with CRITICAL findings
    Given trivy is available on PATH
    And the Terraform directory contains CRITICAL severity misconfigurations
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "FAIL"
    And the JSON notes field indicates CRITICAL findings count
    And the JSON findings field contains titles of CRITICAL issues
    And the command exits with code 2

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator scans configuration with HIGH findings only
    Given trivy is available on PATH
    And the Terraform directory contains HIGH severity misconfigurations
    And the Terraform directory contains no CRITICAL severity misconfigurations
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "WARN"
    And the JSON notes field indicates HIGH findings count
    And the JSON findings field contains titles of HIGH issues
    And the command exits with code 0

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Trivy returns malformed output
    Given trivy is available on PATH
    And trivy returns non-JSON output
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "WARN"
    And the JSON notes field indicates non-JSON output
    And the JSON findings field is an empty list
    And the command exits with code 0

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Trivy fails with unexpected exit code
    Given trivy is available on PATH
    And trivy exits with a code other than 0 or 1
    And trivy produces no stdout
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "WARN"
    And the JSON notes field contains stderr content from trivy
    And the JSON findings field is an empty list
    And the command exits with code 0

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Operator scans configuration with mixed severity findings
    Given trivy is available on PATH
    And the Terraform directory contains CRITICAL severity misconfigurations
    And the Terraform directory contains HIGH severity misconfigurations
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "FAIL"
    And the JSON findings field contains titles of CRITICAL issues
    And the JSON findings field contains titles of HIGH issues
    And the command exits with code 2

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Trivy reports findings with missing title fields
    Given trivy is available on PATH
    And the Terraform directory contains HIGH severity misconfigurations without Title fields
    When the operator runs scan on the Terraform directory
    Then the command outputs valid JSON to stdout
    And the JSON verdict field is "WARN"
    And the JSON findings field contains IDs or fallback text for each finding
    And the command exits with code 0

  @core-domain:verdict-three-state-ladder
  Scenario Outline: Command exit codes align with verdict
    Given trivy is available on PATH
    And the scan produces a <verdict> verdict
    When the operator runs scan on the Terraform directory
    Then the command exits with code <exit_code>

    Examples:
      | verdict | exit_code |
      | PASS    | 0         |
      | WARN    | 0         |
      | FAIL    | 2         |
