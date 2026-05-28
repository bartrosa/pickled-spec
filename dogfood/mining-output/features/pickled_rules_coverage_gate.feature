Feature: Coverage gate verifies rule coverage in Gherkin features
  As a test automation or compliance tool
  I want to verify that a Gherkin feature file adequately covers the rules defined in a ruleset
  So that I can ensure strict rules are tested and detect unknown rule references

  Background:
    Given a ruleset short name "RS"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with no scenarios in feature
    Given a feature with no scenarios
    And a ruleset containing 2 strict rules
    When the coverage gate is executed
    Then the gate result verdict is FAIL
    And all rules appear in unreferenced_rules
    And referenced_rules is empty
    And unknown_references is empty
    And the notes mention unreferenced strict rules

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with all strict rules referenced
    Given a feature with 2 scenarios
    And scenario 1 has tag "RS:rule-1"
    And scenario 2 has tag "RS:rule-2"
    And a ruleset containing 2 strict rules with ids "rule-1" and "rule-2"
    When the coverage gate is executed
    Then the gate result verdict is PASS
    And all strict rules appear in referenced_rules
    And unreferenced_rules is empty
    And unknown_references is empty
    And the notes state all strict rules are referenced and no unknown tags exist

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with unreferenced strict rule
    Given a feature with 1 scenario
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing 2 strict rules with ids "rule-1" and "rule-2"
    When the coverage gate is executed
    Then the gate result verdict is FAIL
    And only rule "rule-1" appears in referenced_rules
    And only rule "rule-2" appears in unreferenced_rules
    And unknown_references is empty
    And the notes include the count of 1 unreferenced strict rule

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with unknown rule reference
    Given a feature with 1 scenario
    And scenario 1 has tag "RS:unknown-rule"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then the gate result verdict is FAIL
    And referenced_rules is empty
    And rule "rule-1" appears in unreferenced_rules
    And unknown_references contains tuple ("RS", "unknown-rule")
    And the unknown_references tuple is sorted
    And the notes include the count of 1 unknown reference
    And the notes include the count of 1 unreferenced strict rule

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with only advisory rules unreferenced
    Given a feature with 1 scenario
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing strict rule "rule-1" and advisory rule "rule-2"
    When the coverage gate is executed
    Then the gate result verdict is PASS
    And only rule "rule-1" appears in referenced_rules
    And only rule "rule-2" appears in unreferenced_rules
    And unknown_references is empty
    And the notes state all strict rules are referenced and no unknown tags exist

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with only informational rules unreferenced
    Given a feature with 1 scenario
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing strict rule "rule-1" and informational rule "rule-2"
    When the coverage gate is executed
    Then the gate result verdict is PASS
    And only rule "rule-1" appears in referenced_rules
    And only rule "rule-2" appears in unreferenced_rules
    And unknown_references is empty
    And the notes state all strict rules are referenced and no unknown tags exist

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Test engineer inspects coverage report structure
    Given a feature with 1 scenario
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then the gate result gate_name is "rules.coverage"
    And the gate result findings is an empty tuple

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Test engineer inspects traces for referenced rules
    Given a feature with 2 scenarios
    And scenario 1 has tag "RS:rule-1"
    And scenario 2 has tag "RS:rule-2"
    And a ruleset containing 2 strict rules with ids "rule-1" and "rule-2"
    When the coverage gate is executed
    Then the gate result traces contains 2 trace objects
    And each referenced rule has a corresponding trace with relation "implements"
    And each trace has confidence "asserted"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Test engineer runs gate with feature having no path
    Given a feature with 1 scenario and no path
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then all traces have artifact_ref "<feature>"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Test engineer runs gate with feature having empty path
    Given a feature with 1 scenario and empty path
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then all traces have artifact_ref "<feature>"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Test engineer runs gate with feature having truthy path
    Given a feature with 1 scenario and path "features/example.feature"
    And scenario 1 has tag "RS:rule-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then all traces have artifact_ref "features/example.feature"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with multiple unknown references
    Given a feature with 2 scenarios
    And scenario 1 has tag "RS:unknown-2"
    And scenario 2 has tag "RS:unknown-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then the gate result verdict is FAIL
    And unknown_references contains tuples in sorted order
    And the first unknown reference is ("RS", "unknown-1")
    And the second unknown reference is ("RS", "unknown-2")

  @rules-domain:unknown-tag-fails-gate
  Scenario: Test engineer runs gate with multiple strict rules and mixed coverage
    Given a feature with 2 scenarios
    And scenario 1 has tag "RS:rule-1"
    And scenario 2 has tag "RS:rule-2"
    And a ruleset containing 3 strict rules with ids "rule-1", "rule-2", and "rule-3"
    When the coverage gate is executed
    Then the gate result verdict is FAIL
    And rules "rule-1" and "rule-2" appear in referenced_rules
    And only rule "rule-3" appears in unreferenced_rules
    And the notes include the count of 1 unreferenced strict rule

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Test engineer runs gate with same rule referenced by multiple scenarios
    Given a feature with 2 scenarios
    And scenario 1 has tag "RS:rule-1"
    And scenario 2 has tag "RS:rule-1"
    And a ruleset containing 1 strict rule with id "rule-1"
    When the coverage gate is executed
    Then the gate result verdict is PASS
    And only rule "rule-1" appears in referenced_rules
    And unreferenced_rules is empty
