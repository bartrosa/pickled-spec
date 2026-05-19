@gdpr-web-crud:right-of-access
@gdpr-web-crud:data-subject-identification
@gdpr-web-crud:audit-logging
@gdpr-web-crud:right-to-rectification
@schema:endpoint:GET-/users/{id}
@schema:endpoint:PATCH-/users/{id}
Feature: Subject access request

  Scenario: Authenticated subject reads their profile
    Given an authenticated user with id "u-456"
    When they GET /users/u-456
    Then the response status is 200 OK
    And the body contains email and name for u-456
    And an audit_log entry records the read

  Scenario: Subject corrects their display name
    Given an authenticated user with id "u-456"
    When they PATCH /users/u-456 with name "Updated Name"
    Then the response status is 200 OK
    And the audit_log records the rectification
