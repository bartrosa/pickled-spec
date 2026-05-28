Feature: Coverage gate for feature files against ruleset
  As a compliance engineer
  I want to verify that my feature files reference all strict rules
  So that I can ensure mandatory requirements are traceable to test scenarios

  Background:
    Given a ruleset with the short name "test-ruleset"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Gate passes when all rules are non-strict
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description        |
      | RULE-01 | advisory    | Advisory rule one  |
      | RULE-02 | guidance    | Guidance rule two  |
    And a feature file with scenarios tagged:
      | scenario_name | tags |
      | First test    |      |
    When the coverage gate is evaluated
    Then the gate verdict is "PASS"
    And the unreferenced rules are:
      | RULE-01 |
      | RULE-02 |
    And the referenced rules are empty
    And the unknown references are empty
    And the gate notes are "All strict rules in test-ruleset are referenced; no unknown reference tags."
    And the findings are empty
    And the gate name is "rules.coverage"
    And the traces are empty

  @rules-domain:unknown-tag-fails-gate
  Scenario: Gate fails when a strict rule is not referenced
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description         |
      | RULE-01 | strict      | Strict rule one     |
      | RULE-02 | advisory    | Advisory rule two   |
    And a feature file with scenarios tagged:
      | scenario_name | tags |
      | First test    |      |
    When the coverage gate is evaluated
    Then the gate verdict is "FAIL"
    And the unreferenced rules are:
      | RULE-01 |
      | RULE-02 |
    And the referenced rules are empty
    And the unknown references are empty
    And the gate notes contain "1 strict rule(s) unreferenced"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Gate fails when a scenario references an unknown rule ID
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And a feature file with scenarios tagged:
      | scenario_name | tags                         |
      | First test    | @REF:test-ruleset:RULE-01    |
      | Second test   | @REF:test-ruleset:RULE-99    |
    When the coverage gate is evaluated
    Then the gate verdict is "FAIL"
    And the referenced rules are:
      | RULE-01 |
    And the unreferenced rules are empty
    And the unknown references are:
      | test-ruleset | RULE-99 |
    And the gate notes contain "1 unknown reference(s)"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Gate passes when all strict rules are referenced and no unknown references exist
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description         |
      | RULE-01 | strict      | Strict rule one     |
      | RULE-02 | advisory    | Advisory rule two   |
      | RULE-03 | strict      | Strict rule three   |
    And a feature file with scenarios tagged:
      | scenario_name | tags                         |
      | First test    | @REF:test-ruleset:RULE-01    |
      | Second test   | @REF:test-ruleset:RULE-03    |
    When the coverage gate is evaluated
    Then the gate verdict is "PASS"
    And the referenced rules are:
      | RULE-01 |
      | RULE-03 |
    And the unreferenced rules are:
      | RULE-02 |
    And the unknown references are empty
    And the gate notes are "All strict rules in test-ruleset are referenced; no unknown reference tags."
    And the traces contain 2 entries
    And each referenced rule has exactly one trace
    And each trace has relation "implements"
    And each trace has confidence "asserted"
    And each trace has artifact_kind "feature"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Unknown references are sorted lexicographically
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And a feature file with scenarios tagged:
      | scenario_name | tags                         |
      | First test    | @REF:test-ruleset:RULE-01    |
      | Second test   | @REF:test-ruleset:RULE-99    |
      | Third test    | @REF:test-ruleset:RULE-10    |
      | Fourth test   | @REF:other-ruleset:RULE-05   |
    When the coverage gate is evaluated
    Then the unknown references are sorted as:
      | other-ruleset | RULE-05 |
      | test-ruleset  | RULE-10 |
      | test-ruleset  | RULE-99 |

  @rules-domain:unknown-tag-fails-gate
  Scenario: A rule referenced multiple times appears once in referenced rules and produces one trace
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And multiple feature files with scenarios tagged:
      | feature_name | scenario_name | tags                      |
      | Feature A    | Test 1        | @REF:test-ruleset:RULE-01 |
      | Feature A    | Test 2        | @REF:test-ruleset:RULE-01 |
      | Feature B    | Test 3        | @REF:test-ruleset:RULE-01 |
    When the coverage gate is evaluated
    Then the referenced rules contain "RULE-01" exactly once
    And the traces contain 1 entry
    And the trace for "RULE-01" has source_id from the ruleset
    And the trace for "RULE-01" has description from the ruleset

  @rules-domain:unknown-tag-fails-gate
  Scenario: Artifact reference defaults to comma-separated feature paths
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And feature files with paths:
      | features/login.feature    |
      | features/checkout.feature |
    And scenarios tagged:
      | scenario_name | tags                      |
      | Test login    | @REF:test-ruleset:RULE-01 |
    And no artifact_ref is provided
    When the coverage gate is evaluated
    Then each trace has artifact_ref "features/login.feature,features/checkout.feature"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Artifact reference defaults to placeholder when features have no paths
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And feature files without paths
    And scenarios tagged:
      | scenario_name | tags                      |
      | Test one      | @REF:test-ruleset:RULE-01 |
    And no artifact_ref is provided
    When the coverage gate is evaluated
    Then each trace has artifact_ref "<features>"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Findings field is always empty
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And a feature file with scenarios tagged:
      | scenario_name | tags |
      | Test one      |      |
    When the coverage gate is evaluated
    Then the findings are empty

  @rules-domain:coverage-union-across-features
  Scenario: Rule is considered referenced if any scenario across any feature references it
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description       |
      | RULE-01 | strict      | Strict rule one   |
      | RULE-02 | strict      | Strict rule two   |
    And multiple feature files with scenarios tagged:
      | feature_name | scenario_name | tags                      |
      | Feature A    | Test A1       |                           |
      | Feature A    | Test A2       | @REF:test-ruleset:RULE-01 |
      | Feature B    | Test B1       | @REF:test-ruleset:RULE-02 |
    When the coverage gate is evaluated
    Then the gate verdict is "PASS"
    And the referenced rules are:
      | RULE-01 |
      | RULE-02 |
    And the unreferenced rules are empty

  @rules-domain:unknown-tag-fails-gate
  Scenario: Gate fails when both strict rules are unreferenced and unknown references exist
    Given the ruleset contains the following rules:
      | rule_id | enforcement | description     |
      | RULE-01 | strict      | Strict rule one |
    And a feature file with scenarios tagged:
      | scenario_name | tags                      |
      | Test one      | @REF:test-ruleset:RULE-99 |
    When the coverage gate is evaluated
    Then the gate verdict is "FAIL"
    And the unreferenced rules are:
      | RULE-01 |
    And the unknown references are:
      | test-ruleset | RULE-99 |
    And the gate notes contain "1 strict rule(s) unreferenced"
    And the gate notes contain "1 unknown reference(s)"

  @rules-domain:unknown-tag-fails-gate
  Scenario: Trace contains all required rule metadata from ruleset
    Given the ruleset contains a rule with:
      | rule_id       | RULE-01                        |
      | enforcement   | strict                         |
      | description   | Test rule description          |
      | source_id     | test-ruleset                   |
      | source_version| 1.0.0                          |
      | locator       | section-2.3                    |
      | active_from   | 2024-01-01                     |
      | applies_to    | all systems                    |
      | source_url    | https://example.com/rules.html |
    And a feature file with scenarios tagged:
      | scenario_name | tags                      |
      | Test one      | @REF:test-ruleset:RULE-01 |
    When the coverage gate is evaluated
    Then the trace for "RULE-01" contains source_reference with:
      | source_id      | test-ruleset                   |
      | source_version | 1.0.0                          |
      | locator        | section-2.3                    |
      | description    | Test rule description          |
      | active_from    | 2024-01-01                     |
      | applies_to     | all systems                    |
      | source_url     | https://example.com/rules.html |
