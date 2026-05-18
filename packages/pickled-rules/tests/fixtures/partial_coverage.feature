Feature: Orders API surface

  @team-api-conv:naming.1
  @team-api-conv:errors.1
  Scenario: Versioned list endpoint returns problem details on error
    Given the orders API is running
    When I GET /v1/orders with invalid parameters
    Then the response uses problem+json
