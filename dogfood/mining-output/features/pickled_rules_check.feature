Feature: Check Gherkin feature files against ruleset

  As a developer or CI system
  I want to verify feature files against a ruleset
  So that behavioral documentation meets defined standards

  Background:
    Given a built-in ruleset "standard" exists
    And a valid ruleset file "custom.yaml" exists
    And a valid feature file "example.feature" exists

  @best-practices:agent-path-first-class
  Scenario: User provides neither feature path nor feature glob
    When the user runs check without feature_path or feature_glob
    Then the command raises ClickException with message "Provide --feature or --feature-glob"

  @pickled-internal:core-llm-cache-default-on
  Scenario: User provides both feature path and feature glob
    When the user runs check with both feature_path and feature_glob
    Then the command raises ClickException with message "Use only one of --feature or --feature-glob"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User provides non-existent ruleset file
    When the user runs check with ruleset "nonexistent.yaml" and feature_path "example.feature"
    Then the command raises ClickException with message "Rule set file not found: nonexistent.yaml"

  @rules-domain:coverage-union-across-features
  Scenario: User provides feature glob matching no files
    When the user runs check with ruleset "standard" and feature_glob "*.nonexistent"
    Then the command raises ClickException with message "No feature files matched"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User provides feature glob matching directories and files
    Given feature_glob "features/**/*.feature" matches files "a.feature", "b.feature" and directory "features"
    When the user runs check with ruleset "standard" and feature_glob "features/**/*.feature"
    Then only file paths are processed
    And files are processed in sorted order

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User checks a single feature file
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard" and feature_path "example.feature"
    Then coverage_gate is called with the parsed feature, ruleset, and short name
    And coverage_gate_features is not called
    And the process exits with status code 0

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User checks multiple feature files
    Given feature_glob "*.feature" matches files "a.feature", "b.feature", "c.feature"
    And all features pass coverage
    When the user runs check with ruleset "standard" and feature_glob "*.feature"
    Then coverage_gate_features is called with the list of parsed features, ruleset, and short name
    And coverage_gate is not called
    And stderr receives message "Union coverage across 3 feature file(s)."
    And the process exits with status code 0

  @rules-domain:coverage-union-across-features
  Scenario: User checks multiple feature files in quiet mode
    Given feature_glob "*.feature" matches files "a.feature", "b.feature"
    And all features pass coverage
    When the user runs check with ruleset "standard", feature_glob "*.feature", and quiet mode
    Then stderr does not receive union coverage message

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: User selects output format
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard", feature_path "example.feature", and output_format "<format>"
    Then the report uses <renderer>

    Examples:
      | format   | renderer                |
      | json     | render_coverage_json    |
      | JSON     | render_coverage_json    |
      | Json     | render_coverage_json    |
      | markdown | render_coverage_markdown|
      | text     | render_coverage_markdown|
      | other    | render_coverage_markdown|

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User runs in quiet mode without output file
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard", feature_path "example.feature", and quiet mode
    Then stdout receives only "PASS: checked 1 feature(s)"
    And the full report is not written to stdout

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User runs in quiet mode with output file
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard", feature_path "example.feature", quiet mode, and output "report.txt"
    Then stdout receives only "PASS: checked 1 feature(s)"
    And the full report is written to file "report.txt"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs with output file but not quiet mode
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard", feature_path "example.feature", and output "report.txt"
    Then the full report is written to file "report.txt"
    And stderr receives message "Report written to report.txt"
    And the full report is not written to stdout

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User runs without output file and not quiet mode
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard" and feature_path "example.feature"
    Then the full report is written to stdout

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Coverage check passes
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard" and feature_path "example.feature"
    Then the process exits with status code 0
    And stdout receives verdict line starting with "PASS:" in quiet mode

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Coverage check fails
    Given feature file "example.feature" fails coverage
    When the user runs check with ruleset "standard" and feature_path "example.feature"
    Then the process exits with status code 1
    And stdout receives verdict line starting with "FAIL:" in quiet mode

  @best-practices:agent-path-first-class
  Scenario: Ruleset name defaults to built-in name when using built-in ruleset
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard" and feature_path "example.feature" without ruleset_name
    Then the short name is "standard"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Ruleset name defaults to file stem when using file path ruleset
    Given a valid ruleset file "CustomRules.yaml" exists
    And feature file "example.feature" passes coverage
    When the user runs check with ruleset "CustomRules.yaml" and feature_path "example.feature" without ruleset_name
    Then the short name is "customrules"

  @best-practices:agent-path-first-class
  Scenario: Ruleset name is explicitly provided
    Given feature file "example.feature" passes coverage
    When the user runs check with ruleset "standard", feature_path "example.feature", and ruleset_name "MyRuleset"
    Then the short name is "myruleset"

  @rules-domain:coverage-union-across-features
  Scenario: Multiple feature files report includes sorted paths
    Given feature_glob "*.feature" matches files "c.feature", "a.feature", "b.feature"
    And all features pass coverage
    When the user runs check with ruleset "standard" and feature_glob "*.feature"
    Then the report includes path label "a.feature,b.feature,c.feature"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Quiet mode shows correct count for multiple files
    Given feature_glob "*.feature" matches files "a.feature", "b.feature", "c.feature"
    And all features fail coverage
    When the user runs check with ruleset "standard", feature_glob "*.feature", and quiet mode
    Then stdout receives only "FAIL: checked 3 feature(s)"
