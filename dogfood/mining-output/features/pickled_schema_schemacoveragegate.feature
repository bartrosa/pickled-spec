Feature: SchemaCoverageGate validates endpoint references in Gherkin feature files

  Background:
    Given a SchemaCoverageGate instance

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects non-dictionary target
    When the gate runs with target "not-a-dict" and context containing feature paths
    Then the verdict is FAIL
    And the notes describe a type mismatch for the target

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects None target
    When the gate runs with target None and context containing feature paths
    Then the verdict is FAIL
    And the notes describe a type mismatch for the target

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects list target
    When the gate runs with target [] and context containing feature paths
    Then the verdict is FAIL
    And the notes describe a type mismatch for the target

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects None context
    When the gate runs with a valid OpenAPI spec target and context None
    Then the verdict is FAIL
    And the notes require feature_paths or feature_texts context keys

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects context missing both required keys
    When the gate runs with a valid OpenAPI spec target and context {}
    Then the verdict is FAIL
    And the notes require feature_paths or feature_texts context keys

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate rejects context with empty lists for both keys
    When the gate runs with a valid OpenAPI spec target and context containing empty feature_paths and empty feature_texts
    Then the verdict is FAIL
    And the notes require feature_paths or feature_texts context keys

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate passes when all endpoint tags match OpenAPI spec paths and methods
    Given an OpenAPI spec with path "/users" and method "get"
    And an OpenAPI spec with path "/users/{id}" and method "post"
    And a feature file containing endpoint tags for "get /users" and "post /users/{id}"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is PASS
    And the notes state "All @schema:endpoint tags have matching paths."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when endpoint tag references path not in spec
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "get /unknown"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings contain a SchemaCoverageFinding for the missing tag
    And the notes list the missing endpoint with tag and source

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when endpoint tag references method not defined for path
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "post /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings contain a SchemaCoverageFinding for the missing tag
    And the notes list the missing endpoint with tag and source

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when spec paths key is missing
    Given an OpenAPI spec without a "paths" key
    And a feature file containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings contain a SchemaCoverageFinding for the missing tag

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate fails when spec paths value is not a dictionary
    Given an OpenAPI spec with "paths" set to "not-a-dict"
    And a feature file containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings contain a SchemaCoverageFinding for the missing tag

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate performs case-insensitive HTTP method matching
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "GET /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is PASS
    And the notes state "All @schema:endpoint tags have matching paths."

  @pickled-internal:core-llm-cache-default-on
  Scenario: Gate reads feature files from feature_paths with UTF-8 encoding
    Given an OpenAPI spec with path "/users" and method "get"
    And a UTF-8 encoded feature file on disk containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the file path in feature_paths
    Then the verdict is PASS
    And the notes state "All @schema:endpoint tags have matching paths."

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate processes feature content from feature_texts
    Given an OpenAPI spec with path "/users" and method "get"
    And feature text containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the feature text in feature_texts
    Then the verdict is PASS
    And the notes state "All @schema:endpoint tags have matching paths."

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate silently skips non-string items in feature_texts
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature_texts list containing non-string items and valid feature text
    When the gate runs with the OpenAPI spec target and context containing the feature_texts
    Then only string items are processed for endpoint tags

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate silently skips non-path-convertible items in feature_paths
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature_paths list containing non-list items and valid file paths
    When the gate runs with the OpenAPI spec target and context containing the feature_paths
    Then only valid path items are processed for endpoint tags

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate reports multiple missing endpoints as semicolon-separated list
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing endpoint tags for "post /users" and "get /orders"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings contain SchemaCoverageFindings for both missing tags
    And the notes list both missing endpoints separated by semicolons

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate includes tag and source in SchemaCoverageFinding objects
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "post /unknown"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And each finding has tag and source attributes

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate uses feature index as source identifier for feature_texts items
    Given an OpenAPI spec with path "/users" and method "get"
    And feature_texts containing an endpoint tag for "post /unknown" at index 2
    When the gate runs with the OpenAPI spec target and context containing the feature_texts
    Then the verdict is FAIL
    And the finding source is "<feature-2>"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate uses file path string as source identifier for feature_paths items
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file at "/path/to/test.feature" containing an endpoint tag for "post /unknown"
    When the gate runs with the OpenAPI spec target and context containing the file path in feature_paths
    Then the verdict is FAIL
    And the finding source is the string representation of the file path

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate returns GateResult with gate_name field set
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the GateResult gate_name equals the gate instance name

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: Gate returns findings only for failure modes with missing endpoints
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "post /unknown"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is FAIL
    And the findings tuple contains SchemaCoverageFinding objects

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Gate returns no findings on successful validation
    Given an OpenAPI spec with path "/users" and method "get"
    And a feature file containing an endpoint tag for "get /users"
    When the gate runs with the OpenAPI spec target and context containing the feature file
    Then the verdict is PASS
    And the findings are empty or not present
