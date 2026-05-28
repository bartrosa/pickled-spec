Feature: Schema coverage verification for endpoint tags

  As a QA engineer or CI pipeline script
  I want to verify that all @schema:endpoint tags in feature files correspond to actual API endpoints
  So that tests stay synchronized with the API schema and runtime failures are prevented

  Background:
    Given an OpenAPI specification document is provided as spec_yaml
    And one or more Cucumber feature file contents are provided as feature_texts

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: QA engineer verifies complete coverage when all endpoint tags exist in specification
    Given spec_yaml defines endpoints "GET /users", "POST /users", and "GET /users/{id}"
    And feature_texts contain tags "@schema:endpoint:GET_users", "@schema:endpoint:POST_users", and "@schema:endpoint:GET_users_id"
    When the schema coverage check is performed
    Then the check returns success
    And no missing endpoint tags are reported

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: QA engineer detects missing endpoints when tags reference undefined endpoints
    Given spec_yaml defines endpoints "GET /users" and "POST /users"
    And feature_texts contain tags "@schema:endpoint:GET_users", "@schema:endpoint:POST_users", and "@schema:endpoint:DELETE_users"
    When the schema coverage check is performed
    Then the check returns failure
    And the missing endpoint tag "@schema:endpoint:DELETE_users" is reported

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: CI pipeline validates multiple missing endpoint tags are all reported
    Given spec_yaml defines endpoint "GET /users"
    And feature_texts contain tags "@schema:endpoint:GET_users", "@schema:endpoint:POST_orders", and "@schema:endpoint:DELETE_products"
    When the schema coverage check is performed
    Then the check returns failure
    And the missing endpoint tags "@schema:endpoint:POST_orders" and "@schema:endpoint:DELETE_products" are reported

  @rules-domain:coverage-union-across-features
  Scenario: QA engineer validates empty feature files without error
    Given spec_yaml defines endpoints "GET /users" and "POST /users"
    And feature_texts are empty or contain no @schema:endpoint tags
    When the schema coverage check is performed
    Then the check returns success
    And no missing endpoint tags are reported

  @schema-domain:openapi-validate-deterministic
  Scenario: CI pipeline handles malformed OpenAPI specification
    Given spec_yaml contains invalid YAML syntax
    And feature_texts contain tag "@schema:endpoint:GET_users"
    When the schema coverage check is performed
    Then the check returns an error
    And an appropriate error message about malformed spec_yaml is provided

  @schema-domain:openapi-validate-deterministic
  Scenario: CI pipeline handles empty OpenAPI specification
    Given spec_yaml is empty or contains no endpoint definitions
    And feature_texts contain tag "@schema:endpoint:GET_users"
    When the schema coverage check is performed
    Then the check returns failure
    And the missing endpoint tag "@schema:endpoint:GET_users" is reported

  @pickled-internal:core-model-from-config-not-hardcoded
  Scenario: QA engineer confirms tool only validates tag-to-spec correspondence
    Given spec_yaml defines endpoint "GET /users"
    And feature_texts contain tag "@schema:endpoint:GET_users" with incomplete or incorrect test implementation
    When the schema coverage check is performed
    Then the check returns success
    And endpoint implementation quality is not validated
    And test correctness is not validated
