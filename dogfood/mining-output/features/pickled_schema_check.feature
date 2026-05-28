Feature: Schema endpoint coverage check command

  Background:
    Given a valid OpenAPI 3.1 specification file "api-spec.yaml"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User provides neither feature_dir nor feature_glob
    When the user runs the check command with spec "api-spec.yaml" and no feature source
    Then the command raises a ClickException with message "Provide --feature-dir or --feature-glob"

  @pickled-internal:core-llm-cache-default-on
  Scenario: User provides both feature_dir and feature_glob
    Given a directory "features/" containing feature files
    When the user runs the check command with spec "api-spec.yaml" and both feature_dir "features/" and feature_glob "tests/**/*.feature"
    Then the command raises a ClickException with message "Use only one of --feature-dir or --feature-glob"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User provides feature_dir with no matching feature files
    Given an empty directory "empty-features/"
    When the user runs the check command with spec "api-spec.yaml" and feature_dir "empty-features/"
    Then the command raises a ClickException with message "No feature files matched"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User provides feature_glob with no matching feature files
    Given a glob pattern "nonexistent/**/*.feature" that matches no files
    When the user runs the check command with spec "api-spec.yaml" and feature_glob "nonexistent/**/*.feature"
    Then the command raises a ClickException with message "No feature files matched"

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: All schema endpoint tags match the OpenAPI specification
    Given a directory "features/" containing feature files with @schema:endpoint tags
    And all @schema:endpoint tags reference endpoints defined in "api-spec.yaml"
    When the user runs the check command with spec "api-spec.yaml" and feature_dir "features/"
    Then the command writes JSON to stdout with verdict "PASS"
    And the JSON output contains keys "gate", "verdict", "notes", and "findings"
    And the command exits with status code 0

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: At least one schema endpoint tag does not match the OpenAPI specification
    Given a directory "features/" containing feature files with @schema:endpoint tags
    And at least one @schema:endpoint tag references an endpoint not defined in "api-spec.yaml"
    When the user runs the check command with spec "api-spec.yaml" and feature_dir "features/"
    Then the command writes JSON to stdout with verdict "FAIL"
    And the JSON output contains keys "gate", "verdict", "notes", and "findings"
    And the findings array includes objects with "tag" and "source" fields for each missing endpoint
    And the command exits with status code 2

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: OpenAPI specification file is OpenAPI 2.0
    Given an OpenAPI 2.0 specification file "swagger-spec.yaml" with "swagger" field
    And a directory "features/" containing feature files
    When the user runs the check command with spec "swagger-spec.yaml" and feature_dir "features/"
    Then the command raises a SchemaParseError

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Specification file is not valid YAML or JSON
    Given a file "invalid-spec.yaml" that is not valid YAML or JSON
    And a directory "features/" containing feature files
    When the user runs the check command with spec "invalid-spec.yaml" and feature_dir "features/"
    Then the command raises a SchemaParseError

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Specification file lacks openapi version field
    Given a valid YAML file "no-version-spec.yaml" without an "openapi" field
    And a directory "features/" containing feature files
    When the user runs the check command with spec "no-version-spec.yaml" and feature_dir "features/"
    Then the command raises a SchemaParseError

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: Verdict is WARN
    Given a directory "features/" containing feature files with @schema:endpoint tags
    And the schema coverage gate returns a verdict of "WARN"
    When the user runs the check command with spec "api-spec.yaml" and feature_dir "features/"
    Then the command writes JSON to stdout with verdict "WARN"
    And the JSON output contains keys "gate", "verdict", "notes", and "findings"
    And the command exits with status code 1

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Feature files discovered via feature_dir are sorted by path
    Given a directory "features/" containing multiple feature files
    When the user runs the check command with spec "api-spec.yaml" and feature_dir "features/"
    Then the command processes feature files in sorted path order

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Feature files discovered via feature_glob are sorted by path
    Given multiple feature files matching the glob pattern "features/**/*.feature"
    When the user runs the check command with spec "api-spec.yaml" and feature_glob "features/**/*.feature"
    Then the command processes feature files in sorted path order

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Feature glob pattern expands recursively and excludes directories
    Given a directory structure with feature files at multiple levels
    And the glob pattern "features/**/*.feature"
    When the user runs the check command with spec "api-spec.yaml" and feature_glob "features/**/*.feature"
    Then only files matching the pattern are included
    And directories are excluded from the match

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: Valid OpenAPI 3.x versions are accepted
    Given a valid OpenAPI <version> specification file "spec.yaml"
    And a directory "features/" containing feature files
    When the user runs the check command with spec "spec.yaml" and feature_dir "features/"
    Then the command processes the specification without raising SchemaParseError

    Examples:
      | version |
      | 3.0     |
      | 3.1     |
      | 3.2     |
