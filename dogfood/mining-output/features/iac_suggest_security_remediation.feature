Feature: IaC Security Remediation Suggestions
  As a security engineer
  I want to receive actionable HCL patch suggestions for Trivy security findings
  So that I can remediate infrastructure-as-code misconfigurations without manual research

  Background:
    Given the iac_suggest_security_remediation tool is available

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Security engineer receives HCL patches for valid Trivy findings
    Given a Trivy config-scan has produced valid JSON findings
    When the security engineer requests remediation suggestions with the Trivy findings JSON
    Then the tool returns suggested HCL patches
    And the patches correspond to the security findings in the JSON

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Security engineer receives context-aware patches when HCL text is provided
    Given a Trivy config-scan has produced valid JSON findings
    And existing HCL configuration text is available
    When the security engineer requests remediation suggestions with both the Trivy findings JSON and the HCL text
    Then the tool returns suggested HCL patches
    And the patches are tailored to the supplied HCL context

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Security engineer receives generic patches when HCL text is omitted
    Given a Trivy config-scan has produced valid JSON findings
    When the security engineer requests remediation suggestions with only the Trivy findings JSON
    Then the tool returns generic HCL remediation patches
    And the patches are based solely on the Trivy findings

  @best-practices:llm-drafter-temperature-zero
  Scenario: Security engineer submits Trivy findings with zero security issues
    Given a Trivy config-scan has produced JSON with zero findings
    When the security engineer requests remediation suggestions with the empty findings JSON
    Then the tool completes without error
    And no patches are suggested

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Security engineer submits Trivy findings with multiple security issues
    Given a Trivy config-scan has produced JSON with multiple findings
    When the security engineer requests remediation suggestions with the findings JSON
    Then the tool returns suggested HCL patches
    And patches are provided for each finding in the JSON

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Tool validates Trivy JSON schema before processing
    Given an invalid JSON document that does not conform to Trivy output schema
    When the security engineer requests remediation suggestions with the invalid JSON
    Then the tool reports a validation error
    And no patches are suggested

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Suggested patches are suitable for applying to HCL files
    Given a Trivy config-scan has produced valid JSON findings
    When the security engineer requests remediation suggestions with the Trivy findings JSON
    Then the tool returns suggested HCL patches
    And the patches are in a format suitable for applying to HCL configuration files
