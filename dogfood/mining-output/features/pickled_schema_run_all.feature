Feature: Schema validation and coverage gate
  As a build engineer
  I want to validate OpenAPI specs and measure schema coverage
  So that I can ensure API specifications are correct and comprehensively tested

  Background:
    Given the pickled-schema package is installed with openapi extras

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate in directory with no spec files
    Given a working directory with no specs subdirectory
    When the run_all gate is executed
    Then a single result is returned
    And the result has gate_name "schema.openapi"
    And the result has verdict WARN
    And the result has notes "no specs/*.yaml"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate in directory with empty specs subdirectory
    Given a working directory with an empty specs subdirectory
    When the run_all gate is executed
    Then a single result is returned
    And the result has gate_name "schema.openapi"
    And the result has verdict WARN
    And the result has notes "no specs/*.yaml"

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User validates a valid OpenAPI 3.0 specification
    Given a working directory with specs subdirectory
    And a file "specs/example.yaml" containing valid OpenAPI 3.0 content
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.example.yaml" is returned
    And the notes contain the relative path to the spec

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User validates a valid OpenAPI 3.1 specification
    Given a working directory with specs subdirectory
    And a file "specs/api.yaml" containing valid OpenAPI 3.1 content
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned

  @pickled-internal:stdio-hygiene-gates-log-stderr
  Scenario: User validates a valid OpenAPI 3.2 specification
    Given a working directory with specs subdirectory
    And a file "specs/service.yml" containing valid OpenAPI 3.2 content
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.service.yml" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to validate a malformed YAML file
    Given a working directory with specs subdirectory
    And a file "specs/broken.yaml" containing invalid YAML syntax
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.broken.yaml" is returned
    And the notes contain the parse error message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to validate a spec with non-dict root
    Given a working directory with specs subdirectory
    And a file "specs/list.yaml" containing a YAML list at root level
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.list.yaml" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to validate an OpenAPI 2.0 specification
    Given a working directory with specs subdirectory
    And a file "specs/swagger.yaml" containing a spec with "swagger" field
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.swagger.yaml" is returned
    And the notes mention OpenAPI 2.0 is unsupported

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User attempts to validate a spec without openapi field
    Given a working directory with specs subdirectory
    And a file "specs/missing.yaml" containing a dict without "openapi" field
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.missing.yaml" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario Outline: User attempts to validate a spec with unsupported OpenAPI version
    Given a working directory with specs subdirectory
    And a file "specs/version.yaml" with openapi field "<version>"
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.version.yaml" is returned

    Examples:
      | version |
      | 2.0     |
      | 4.0     |
      | 3.3     |
      | 1.0     |

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User validates multiple valid specs
    Given a working directory with specs subdirectory
    And a file "specs/a-first.yaml" containing valid OpenAPI 3.0 content
    And a file "specs/b-second.yaml" containing valid OpenAPI 3.1 content
    And a file "specs/c-third.yaml" containing valid OpenAPI 3.2 content
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.a-first.yaml" is returned
    And a PASS result with gate_name "schema.openapi.validate.b-second.yaml" is returned
    And a PASS result with gate_name "schema.openapi.validate.c-third.yaml" is returned
    And a WARN result with gate_name "schema.openapi.note" is returned
    And the WARN notes indicate multiple specs were found
    And the WARN notes indicate the first spec will be used for coverage

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate with valid spec but no feature files
    Given a working directory with specs subdirectory
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    And no features subdirectory exists
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned
    And no result with gate_name containing "schema.coverage" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate with valid spec and empty features directory
    Given a working directory with specs subdirectory
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    And an empty features subdirectory
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned
    And no result with gate_name containing "schema.coverage" is returned

  # TODO: SchemaCoverageGate behavior is unresolved; assuming it returns verdict, findings, notes
  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate with valid spec and feature files
    Given a working directory with specs subdirectory
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    And a features subdirectory with feature files
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned
    And a result with gate_name "schema.coverage" is returned
    And the coverage result verdict is from the SchemaCoverageGate
    And the coverage result findings are from the SchemaCoverageGate
    And the coverage result notes default to the spec relative path if SchemaCoverageGate provides none

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate without openapi-spec-validator installed
    Given a working directory with specs subdirectory
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    And the openapi-spec-validator package is not installed
    When the run_all gate is executed
    Then a SchemaValidationError is raised

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate and receives results in deterministic order
    Given a working directory with specs subdirectory
    And a file "specs/z-last.yaml" containing valid OpenAPI 3.0 content
    And a file "specs/a-first.yaml" containing valid OpenAPI 3.1 content
    And a file "specs/m-middle.yaml" containing valid OpenAPI 3.2 content
    And a features subdirectory with feature files
    When the run_all gate is executed
    Then results are returned in order: validation results lexicographically by filename, then multi-spec warning, then coverage result
    And the validation results appear as "a-first.yaml", "m-middle.yaml", "z-last.yaml"

  @pickled-internal:mcp-output-fixed-json-shape
  Scenario: User validates spec file with .json extension
    Given a working directory with specs subdirectory
    And a file "specs/api.json" containing valid OpenAPI 3.0 JSON content
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.api.json" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User validates spec file with unknown extension
    Given a working directory with specs subdirectory
    And a file "specs/api.txt" containing valid OpenAPI 3.0 YAML content
    When the run_all gate is executed
    Then the file is parsed as YAML
    And a PASS result with gate_name "schema.openapi.validate.api.txt" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate where spec file cannot be read
    Given a working directory with specs subdirectory
    And a file "specs/unreadable.yaml" that triggers an OSError when read
    When the run_all gate is executed
    Then a FAIL result with gate_name "schema.openapi.validate.unreadable.yaml" is returned
    And the notes contain the OS error message

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate with workdir as string path
    Given a working directory path provided as a string
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    When the run_all gate is executed with the string path
    Then the path is resolved to an absolute Path
    And a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User runs gate with workdir as Path object
    Given a working directory path provided as a Path object
    And a file "specs/api.yaml" containing valid OpenAPI 3.0 content
    When the run_all gate is executed with the Path object
    Then the path is resolved to an absolute Path
    And a PASS result with gate_name "schema.openapi.validate.api.yaml" is returned

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: User validates mix of valid and invalid specs
    Given a working directory with specs subdirectory
    And a file "specs/valid.yaml" containing valid OpenAPI 3.0 content
    And a file "specs/invalid.yaml" containing invalid YAML syntax
    When the run_all gate is executed
    Then a PASS result with gate_name "schema.openapi.validate.valid.yaml" is returned
    And a FAIL result with gate_name "schema.openapi.validate.invalid.yaml" is returned
    And only the valid spec is used for coverage analysis
