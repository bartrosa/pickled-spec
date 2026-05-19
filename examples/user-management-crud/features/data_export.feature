@gdpr-web-crud:right-to-portability
@gdpr-web-crud:data-subject-identification
@schema:endpoint:GET-/users/{id}/export
Feature: Data portability export

  Scenario: Subject downloads a machine-readable export
    Given an authenticated user with id "u-789"
    When they GET /users/u-789/export
    Then the response status is 200 OK
    And the Content-Type is application/json
    And the payload includes id, email, name, and consent fields
