Feature: check-all command validates entire workspace using all registered gates

  Background:
    Given a workspace directory exists

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer runs check-all without arguments
    When the developer runs check-all without specifying a workdir
    Then check-all uses the current directory as the workspace root
    And check-all discovers all gates from installed pickled-* packages
    And check-all executes all discovered gates
    And check-all reports verdicts from all gates

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer runs check-all with a specific workdir
    Given a workspace directory at "/path/to/workspace"
    When the developer runs check-all with workdir "/path/to/workspace"
    Then check-all uses "/path/to/workspace" as the workspace root
    And check-all discovers all gates from installed pickled-* packages
    And check-all executes all discovered gates
    And check-all reports verdicts from all gates

  @core-domain:verdict-three-state-ladder
  Scenario: Developer runs check-all and all gates pass
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And all registered gates will pass
    When the developer runs check-all
    Then check-all exits with code 0

  @data-domain:migration-drift-gate
  Scenario: Developer runs check-all and at least one gate fails
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And at least one registered gate will fail
    When the developer runs check-all
    Then check-all exits with a non-zero code

  @core-domain:verdict-three-state-ladder
  Scenario: Developer runs check-all with warnings and warn_ok is false
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And gates will produce only WARN verdicts
    When the developer runs check-all with warn_ok set to false
    Then check-all exits with a non-zero code

  @core-domain:verdict-three-state-ladder
  Scenario: Developer runs check-all with warnings and warn_ok is omitted
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And gates will produce only WARN verdicts
    When the developer runs check-all without specifying warn_ok
    Then check-all exits with a non-zero code

  @core-domain:verdict-three-state-ladder
  Scenario: Developer runs check-all with warnings and warn_ok is true
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And gates will produce only WARN verdicts
    When the developer runs check-all with warn_ok set to true
    Then check-all exits with code 0

  @core-domain:verdict-three-state-ladder
  Scenario: CI pipeline runs check-all with mixed PASS and WARN verdicts and warn_ok is true
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And some gates will pass
    And some gates will produce WARN verdicts
    When the CI pipeline runs check-all with warn_ok set to true
    Then check-all exits with code 0

  @core-domain:verdict-three-state-ladder
  Scenario: CI pipeline runs check-all with FAIL and WARN verdicts regardless of warn_ok
    Given a valid workspace with features/, specs/, infra/, and migrations/ directories
    And some gates will fail
    And some gates will produce WARN verdicts
    When the CI pipeline runs check-all with warn_ok set to true
    Then check-all exits with a non-zero code

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: Developer runs check-all and gates from multiple pickled-* packages are executed
    Given multiple pickled-* packages are installed
    And each package registers gates
    When the developer runs check-all
    Then check-all executes gates from all installed pickled-* packages
    And check-all reports verdicts from gates across all packages
