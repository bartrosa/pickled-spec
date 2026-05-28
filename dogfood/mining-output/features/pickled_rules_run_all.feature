Feature: Run All Coverage Gates for Configured Rulesets
  As a quality assurance engineer
  I want to verify that all strict enforcement rules are covered by feature scenarios
  So that I can ensure traceability between requirements and tests

  Background:
    Given a working directory with BDD feature files

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with missing configuration file
    Given the pickled.ruleset.yaml file does not exist
    When the gate runs against the working directory
    Then a single WARN result is returned
    And the result has gate_name "rules.coverage"
    And the result notes mention "missing pickled.ruleset.yaml or ruleset/rulesets key"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with empty configuration
    Given the pickled.ruleset.yaml file is empty
    When the gate runs against the working directory
    Then a single WARN result is returned
    And the result has gate_name "rules.coverage"
    And the result notes mention "missing pickled.ruleset.yaml or ruleset/rulesets key"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with both ruleset keys present
    Given the pickled.ruleset.yaml file contains both "ruleset" and "rulesets" keys
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes describe mutual exclusivity violation

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with non-string ruleset value
    Given the pickled.ruleset.yaml file contains "ruleset" key with a non-string value
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes contain a validation message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with non-list rulesets value
    Given the pickled.ruleset.yaml file contains "rulesets" key with a non-list value
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes contain a validation message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with empty rulesets list
    Given the pickled.ruleset.yaml file contains "rulesets" key with an empty list
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes require at least one entry

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with malformed ruleset entry
    Given the pickled.ruleset.yaml file contains "rulesets" with a non-dict entry
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes contain a descriptive validation message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with missing path in ruleset entry
    Given the pickled.ruleset.yaml file contains "rulesets" with an entry missing "path"
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes contain a descriptive validation message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with duplicate short names
    Given the pickled.ruleset.yaml file contains "rulesets" with duplicate short_name values
    When the gate runs against the working directory
    Then a single FAIL result is returned
    And the result notes identify the duplicate positions

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with no matching feature files
    Given the pickled.ruleset.yaml file is valid
    And no feature files match the configured glob pattern
    When the gate runs against the working directory
    Then a single WARN result is returned
    And the result notes mention "no feature files"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with single ruleset configured
    Given the pickled.ruleset.yaml file contains a single "ruleset" key
    And the ruleset file exists
    And feature files exist
    When the gate runs against the working directory
    Then a result is returned with gate_name "rules.coverage"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with multiple rulesets configured
    Given the pickled.ruleset.yaml file contains "rulesets" with multiple entries
    And all ruleset files exist
    And feature files exist
    When the gate runs against the working directory
    Then results are returned for each ruleset
    And each result has gate_name "rules.coverage.{short_name}"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with missing ruleset file
    Given the pickled.ruleset.yaml file references a ruleset that does not exist
    When the gate runs against the working directory
    Then a FAIL result is returned
    And the result notes indicate the missing file path

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with invalid ruleset YAML
    Given the pickled.ruleset.yaml file is valid
    And a referenced ruleset file contains invalid YAML
    When the gate runs against the working directory
    Then a FAIL result is returned
    And the result has gate_name "rules.load.{short_name}"
    And the result notes contain the validation error message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with all strict rules referenced
    Given the pickled.ruleset.yaml file is valid
    And all ruleset files exist and are valid
    And feature scenarios reference all strict-enforcement rules
    And no unknown rule references exist
    When the gate runs against the working directory
    Then a PASS result is returned
    And the result includes traces for each referenced rule
    And each trace has relation "implements"
    And each trace has artifact_kind "feature"
    And each trace has confidence "asserted"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with unreferenced strict rules
    Given the pickled.ruleset.yaml file is valid
    And all ruleset files exist and are valid
    And one or more strict-enforcement rules are not referenced by any scenario
    When the gate runs against the working directory
    Then a FAIL result is returned
    And the result notes contain the count of unreferenced rules

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with unknown rule references
    Given the pickled.ruleset.yaml file is valid
    And all ruleset files exist and are valid
    And feature scenarios reference rule IDs not in the ruleset
    When the gate runs against the working directory
    Then a FAIL result is returned
    And the result notes contain the count of unknown references

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Quality engineer runs coverage with both unreferenced and unknown rules
    Given the pickled.ruleset.yaml file is valid
    And all ruleset files exist and are valid
    And some strict-enforcement rules are unreferenced
    And some scenario tags reference unknown rule IDs
    When the gate runs against the working directory
    Then a FAIL result is returned
    And the result notes contain both unreferenced and unknown rule counts

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate always returns non-empty result list
    Given any valid or invalid configuration state
    When the gate runs against the working directory
    Then at least one GateResult object is returned
