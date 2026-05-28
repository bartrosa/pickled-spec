Feature: Security Baseline Gate validates Terraform configurations for HIGH and CRITICAL misconfigurations

  As a quality assurance pipeline
  I want to scan Infrastructure-as-Code for security misconfigurations
  So that I can prevent insecure Terraform configurations from being deployed

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects non-Path target with FAIL verdict
    Given a target that is not a Path instance
    When the security baseline gate runs
    Then the gate returns a FAIL verdict
    And the notes contain the actual type name of the target

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes gracefully when trivy is not installed
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is not found on the system PATH
    When the security baseline gate runs
    Then the gate returns a PASS verdict
    And the notes indicate the scan was skipped

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate warns when trivy exits with unexpected return code and empty stdout
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy exits with a return code other than 0 or 1
    And trivy produces empty stdout
    When the security baseline gate runs
    Then the gate returns a WARN verdict
    And the notes contain the stderr content from trivy

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate warns when trivy output is not valid JSON
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy produces output that is not valid JSON
    When the security baseline gate runs
    Then the gate returns a WARN verdict
    And the notes indicate the output was non-JSON

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when trivy reports CRITICAL misconfigurations
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy reports one or more CRITICAL severity misconfigurations
    When the security baseline gate runs
    Then the gate returns a FAIL verdict
    And the findings contain the titles of all CRITICAL misconfigurations
    And the notes report the count of CRITICAL findings

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate warns when trivy reports HIGH but no CRITICAL misconfigurations
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy reports one or more HIGH severity misconfigurations
    And trivy reports no CRITICAL severity misconfigurations
    When the security baseline gate runs
    Then the gate returns a WARN verdict
    And the findings contain the titles of all HIGH misconfigurations
    And the notes report the count of HIGH findings

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes when trivy reports no HIGH or CRITICAL misconfigurations
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy reports no HIGH or CRITICAL severity misconfigurations
    When the security baseline gate runs
    Then the gate returns a PASS verdict
    And the notes confirm no HIGH or CRITICAL findings were detected

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate ignores context parameter
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And a context dictionary is provided
    And trivy reports no HIGH or CRITICAL severity misconfigurations
    When the security baseline gate runs
    Then the gate returns a PASS verdict
    And the verdict is not influenced by the context parameter

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Gate invokes trivy with correct arguments
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    When the security baseline gate runs
    Then trivy is invoked with the config subcommand
    And trivy receives the target path as a string argument
    And trivy receives the argument --format json
    And trivy receives the argument --severity HIGH,CRITICAL
    And trivy receives the argument --quiet

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate handles malformed trivy JSON output gracefully
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy output contains non-dict entries in Results array
    When the security baseline gate runs
    Then the gate silently skips non-dict Results entries
    And the gate continues processing valid entries

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate handles malformed Misconfigurations array gracefully
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy output contains non-dict entries in Misconfigurations array
    When the security baseline gate runs
    Then the gate silently skips non-dict Misconfigurations entries
    And the gate continues processing valid entries

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Gate compares severity case-insensitively
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And trivy reports a misconfiguration with severity "<reported_severity>"
    When the security baseline gate runs
    Then the misconfiguration is classified as <expected_classification>

    Examples:
      | reported_severity | expected_classification |
      | CRITICAL          | CRITICAL                |
      | critical          | CRITICAL                |
      | CrItIcAl          | CRITICAL                |
      | HIGH              | HIGH                    |
      | high              | HIGH                    |
      | HiGh              | HIGH                    |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario Outline: Gate extracts finding title with fallback logic
    Given a valid Path target pointing to a Terraform directory
    And the trivy executable is available
    And a misconfiguration has Title field "<title_value>"
    And the misconfiguration has ID field "<id_value>"
    When the security baseline gate processes the misconfiguration
    Then the finding title is "<expected_title>"

    Examples:
      | title_value       | id_value      | expected_title    |
      | Security Issue    | CVE-2023-0001 | Security Issue    |
      |                   | CVE-2023-0001 | CVE-2023-0001     |
      |                   |               | finding           |
