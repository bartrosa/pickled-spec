Feature: Batch validation of BDD feature files

  As a quality-gate orchestrator
  I want to validate all Gherkin feature files in a project
  So that I can detect parsing errors before runtime without requiring an LLM connection

  Background:
    Given a project workspace directory

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Project contains no features directory
    When no features directory exists under the workspace
    Then the validation returns a single result
    And the result has gate name "bdd.features"
    And the result has verdict "PASS"
    And the result notes indicate no features directory was found

  @data-domain:migration-drift-gate
  Scenario: Project contains an empty features directory
    Given a features directory exists under the workspace
    But no feature files exist in the features directory
    When validation runs
    Then the validation returns a single result
    And the result has gate name "bdd.features"
    And the result has verdict "PASS"
    And the result notes indicate no features directory was found

  @best-practices:agent-path-first-class
  Scenario: Project contains a single valid feature file
    Given a feature file "login.feature" with valid Gherkin content exists
    When validation runs
    Then the validation returns two results
    And the first result has gate name "bdd.parse.login.feature"
    And the first result has verdict "PASS"
    And the first result notes contain the relative file path
    And the second result has gate name "bdd.ambiguity"
    And the second result has verdict "PASS"
    And the second result notes indicate ambiguity check is skipped

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Project contains multiple valid feature files
    Given feature files exist at multiple directory depths:
      | path                              |
      | features/authentication.feature   |
      | features/admin/users.feature      |
      | features/admin/roles.feature      |
    And all feature files contain valid Gherkin
    When validation runs
    Then the validation returns four results
    And results are ordered by sorted file path
    And each feature file has a corresponding PASS result with gate name "bdd.parse.<filename>"
    And the final result has gate name "bdd.ambiguity" with verdict "PASS"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario Outline: Feature file with parsing errors
    Given a feature file "<filename>" exists
    And the file content is <condition>
    When validation runs
    Then a result exists with gate name "bdd.parse.<filename>"
    And that result has verdict "FAIL"
    And that result notes contain "<error_message>"
    And the validation completes without raising exceptions
    And the final result has gate name "bdd.ambiguity" with verdict "PASS"

    Examples:
      | filename        | condition             | error_message                |
      | empty.feature   | empty                 | Gherkin text is empty        |
      | blank.feature   | whitespace only       | Gherkin text is empty        |
      | invalid.feature | missing Feature block | No Feature found in Gherkin text |

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Mixed valid and invalid feature files
    Given feature files exist:
      | filename       | status  |
      | valid.feature  | valid   |
      | empty.feature  | empty   |
      | valid2.feature | valid   |
      | broken.feature | invalid |
    When validation runs
    Then the validation returns five results
    And results for valid files have verdict "PASS"
    And results for invalid files have verdict "FAIL"
    And invalid file results contain error details in notes
    And the final result has gate name "bdd.ambiguity" with verdict "PASS"
    And validation completes without raising exceptions

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: All feature files fail to parse
    Given multiple feature files exist
    But all feature files contain parsing errors
    When validation runs
    Then all feature file results have verdict "FAIL"
    And each FAIL result notes contain the corresponding error message
    And the final result has gate name "bdd.ambiguity" with verdict "PASS"
    And validation completes without raising exceptions

  @best-practices:agent-path-first-class
  Scenario: Feature files in nested subdirectories are discovered
    Given feature files exist in deeply nested paths:
      | path                                    |
      | features/smoke/critical.feature         |
      | features/regression/api/endpoints.feature |
      | features/regression/ui/flows.feature    |
    When validation runs
    Then all nested feature files are validated
    And results are returned in sorted path order

  # TODO: Clarify behavior when workdir is invalid or inaccessible (permission errors, non-existent path)
  # TODO: Clarify exact format of relative path in notes for passing files
  # TODO: Document whether symbolic links in features/ are followed
