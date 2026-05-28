Feature: Differential verification against oracle implementation
  As a tester or developer
  I want to verify a candidate implementation against a reference oracle
  So that I can ensure behavioral compatibility across a test corpus

  Background:
    Given the diff_verify_against_oracle tool is available

  @diff-domain:differential-oracle-gate
  Scenario: Developer verifies candidate matches oracle for all corpus items
    Given an oracle command "reference-tool --process"
    And a candidate command "new-tool --process"
    And a corpus with items "input1.txt, input2.txt, input3.txt"
    When the verification is executed
    Then both commands are run against each corpus item
    And the outputs are compared for differences
    And a verification report is returned

  @diff-domain:differential-oracle-gate
  Scenario: Developer detects differences between candidate and oracle
    Given an oracle command "reference-tool --process"
    And a candidate command "buggy-tool --process"
    And a corpus with items "test1.txt, test2.txt"
    And the candidate produces different output for "test2.txt"
    When the verification is executed
    Then differences are reported for "test2.txt"
    And the oracle output is included in the report
    And the candidate output is included in the report

  @diff-domain:differential-oracle-gate
  Scenario: Developer customizes difference detection with comparator
    Given an oracle command "reference-tool --format"
    And a candidate command "new-tool --format"
    And a corpus with items "data1.json, data2.json"
    And a custom comparator "json-semantic-compare"
    When the verification is executed
    Then the custom comparator is used to detect differences
    And differences are reported according to the comparator logic

  @diff-domain:differential-oracle-gate
  Scenario: Developer limits execution time with timeout
    Given an oracle command "slow-reference --compute"
    And a candidate command "fast-candidate --compute"
    And a corpus with items "large-input.dat"
    And a timeout of 30 seconds per command
    When the verification is executed
    Then each command execution is limited to 30 seconds
    And timeout violations are reported if they occur

  @diff-domain:differential-oracle-gate
  Scenario Outline: Tool validates required parameters
    Given <missing_parameter> is not provided
    When the verification is attempted
    Then the tool returns a parameter validation error
    And the error indicates <missing_parameter> is required

    Examples:
      | missing_parameter  |
      | oracle_command     |
      | candidate_command  |
      | corpus_items       |

  @diff-domain:differential-oracle-gate
  Scenario: Developer runs verification with minimal required parameters
    Given an oracle command "baseline-tool"
    And a candidate command "comparison-tool"
    And a corpus with items "test.dat"
    When the verification is executed without optional parameters
    Then both commands are run against each corpus item
    And default comparison logic is applied
    And a verification report is returned

  @diff-domain:differential-oracle-gate
  Scenario: Developer verifies with empty corpus
    Given an oracle command "oracle-cmd"
    And a candidate command "candidate-cmd"
    And a corpus with no items
    When the verification is executed
    Then no command executions occur
    And the report indicates zero items were tested
